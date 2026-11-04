import SwiftUI
import UIKit
import SceneKit

// MARK: - App

@main
struct MinecraftLikeApp: App {
    @StateObject private var controller = GameController()

    var body: some Scene {
        WindowGroup {
            ContentView(controller: controller)
        }
    }
}

// MARK: - Content

struct ContentView: View {
    @ObservedObject var controller: GameController

    var body: some View {
        ZStack {
            GameSceneView(controller: controller)
                .ignoresSafeArea()

            VStack {
                HStack {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("3D Minecraft-like Sandbox")
                            .font(.headline)
                        Text("左: 移動 / 右: 視点 / JUMP: 跳ぶ / BREAK・PLACE: 破壊・設置")
                            .font(.caption2)
                            .foregroundColor(.white.opacity(0.85))
                    }
                    .padding(.horizontal, 10)
                    .padding(.vertical, 6)
                    .background(.black.opacity(0.25), in: RoundedRectangle(cornerRadius: 10))
                    Spacer()
                }
                .padding(.top, 44)

                Spacer()

                HStack(alignment: .bottom) {
                    JoystickView(controller: controller)
                        .padding(.leading, 18)

                    Spacer()

                    ActionButtonsView(controller: controller)
                        .padding(.trailing, 14)
                }
                .padding(.bottom, 18)

                HotbarView(controller: controller)
                    .padding(.bottom, 18)
            }
        }
        .statusBarHidden(true)
    }
}

// MARK: - Blocks

enum Block: Int, CaseIterable, Identifiable {
    case air = 0
    case grass = 1
    case dirt = 2
    case stone = 3
    case wood = 4
    case leaves = 5
    case sand = 6
    case glass = 7
    case brick = 8

    var id: Int { rawValue }

    var emoji: String {
        switch self {
        case .air: return "⬜"
        case .grass: return "🌱"
        case .dirt: return "🟫"
        case .stone: return "⛰️"
        case .wood: return "🪵"
        case .leaves: return "🍃"
        case .sand: return "🏖️"
        case .glass: return "🪟"
        case .brick: return "🧱"
        }
    }

    var color: Color {
        switch self {
        case .air:
            return Color.gray.opacity(0.2)
        case .grass:
            return Color(red: 0.31, green: 0.65, blue: 0.30)
        case .dirt:
            return Color(red: 0.42, green: 0.29, blue: 0.18)
        case .stone:
            return Color(red: 0.54, green: 0.56, blue: 0.60)
        case .wood:
            return Color(red: 0.35, green: 0.23, blue: 0.15)
        case .leaves:
            return Color(red: 0.18, green: 0.48, blue: 0.21)
        case .sand:
            return Color(red: 0.86, green: 0.80, blue: 0.58)
        case .glass:
            return Color.white.opacity(0.22)
        case .brick:
            return Color(red: 0.68, green: 0.28, blue: 0.22)
        }
    }
}

// MARK: - World

final class World {
    static let W = 64
    static let H = 40
    static let D = 64
    static let CS = 8

    var blocks = [UInt8](repeating: 0, count: W * H * D)

    func index(_ x: Int, _ y: Int, _ z: Int) -> Int {
        (x * D + z) * H + y
    }

    func inBounds(_ x: Int, _ y: Int, _ z: Int) -> Bool {
        x >= 0 && x < Self.W && y >= 0 && y < Self.H && z >= 0 && z < Self.D
    }

    func get(_ x: Int, _ y: Int, _ z: Int) -> Block {
        guard inBounds(x, y, z) else { return .air }
        return Block(rawValue: Int(blocks[index(x, y, z)])) ?? .air
    }

    func set(_ x: Int, _ y: Int, _ z: Int, _ block: Block) {
        guard inBounds(x, y, z) else { return }
        blocks[index(x, y, z)] = UInt8(block.rawValue)
    }

    func isSolid(_ x: Int, _ y: Int, _ z: Int) -> Bool {
        if y < 0 { return true }
        if x < 0 || x >= Self.W || z < 0 || z >= Self.D { return true }
        if y >= Self.H { return true }
        return get(x, y, z) != .air
    }

    func faceVisible(current: Block, neighbor: Block) -> Bool {
        if current == .glass {
            return neighbor == .air
        }
        return neighbor == .air
    }

    func topY(_ x: Int, _ z: Int) -> Int {
        for y in stride(from: Self.H - 1, through: 0, by: -1) {
            if get(x, y, z) != .air {
                return y
            }
        }
        return 0
    }

    func generate() {
        blocks = [UInt8](repeating: 0, count: Self.W * Self.H * Self.D)

        for x in 0..<Self.W {
            for z in 0..<Self.D {
                let h = terrainHeight(x: x, z: z)

                for y in 0..<h {
                    var b: Block = .stone

                    if y == h - 1 {
                        b = (h < 12) ? .sand : .grass
                    } else if y >= h - 4 {
                        b = .dirt
                    }

                    set(x, y, z, b)
                }
            }
        }

        for x in 3..<(Self.W - 3) {
            for z in 3..<(Self.D - 3) {
                let top = topY(x, z)
                guard get(x, top, z) == .grass else { continue }

                let r = hash01(Float(x) * 12.9898, Float(z) * 78.233)
                if r > 0.984 {
                    makeTree(x: x, y: top + 1, z: z, seed: r)
                }
            }
        }
    }

    func terrainHeight(x: Int, z: Int) -> Int {
        let xf = Float(x)
        let zf = Float(z)

        let big = noise2D(x: xf * 0.035, z: zf * 0.035)
        let small = noise2D(x: xf * 0.095, z: zf * 0.095)
        let wave = sin(xf * 0.11) * 1.3 + cos(zf * 0.10) * 1.3

        var h = Int(17 + (big - 0.5) * 13 + (small - 0.5) * 7 + wave)
        h = max(3, min(30, h))
        return h
    }

    func makeTree(x: Int, y: Int, z: Int, seed: Float) {
        let trunk = 4 + Int((seed * 100).truncatingRemainder(dividingBy: 3))

        for i in 0..<trunk {
            set(x, y + i, z, .wood)
        }

        let leafY = y + trunk
        for dx in -2...2 {
            for dz in -2...2 {
                for dy in -1...1 {
                    let nx = x + dx
                    let ny = leafY + dy
                    let nz = z + dz

                    if abs(dx) + abs(dz) == 4 && dy == 1 {
                        continue
                    }

                    if get(nx, ny, nz) == .air {
                        set(nx, ny, nz, .leaves)
                    }
                }
            }
        }
    }

    // MARK: Noise

    func hash01(_ x: Float, _ y: Float) -> Float {
        let s = sin(x * 127.1 + y * 311.7) * 43758.5453123
        return s - floor(s)
    }

    func smoothstep(_ t: Float) -> Float {
        t * t * (3 - 2 * t)
    }

    func lerp(_ a: Float, _ b: Float, _ t: Float) -> Float {
        a + (b - a) * t
    }

    func noise2D(x: Float, z: Float) -> Float {
        let xi = Int(floor(x))
        let zi = Int(floor(z))
        let xf = x - Float(xi)
        let zf = z - Float(zi)

        let a = hash01(Float(xi), Float(zi))
        let b = hash01(Float(xi + 1), Float(zi))
        let c = hash01(Float(xi), Float(zi + 1))
        let d = hash01(Float(xi + 1), Float(zi + 1))

        let u = smoothstep(xf)
        let v = smoothstep(zf)

        return lerp(lerp(a, b, u), lerp(c, d, u), v)
    }
}

// MARK: - Geometry

struct FaceDef {
    let vertices: [SCNVector3]
    let normal: SCNVector3
}

func materialIndex(for b: Block) -> Int {
    switch b {
    case .grass: return 0
    case .dirt: return 1
    case .stone: return 2
    case .wood: return 3
    case .leaves: return 4
    case .sand: return 5
    case .glass: return 6
    case .brick: return 7
    case .air: return 0
    }
}

struct MeshBuilder {
    static func buildChunk(
        world: World,
        cx: Int,
        cz: Int,
        materials: [SCNMaterial]
    ) -> SCNNode {
        var positions: [SCNVector3] = []
        var normals: [SCNVector3] = []
        var uv: [SCNVector2] = []
        var indicesByMaterial: [[Int]] = Array(repeating: [], count: 8)

        let x0 = cx * World.CS
        let x1 = min(x0 + World.CS, World.W)
        let z0 = cz * World.CS
        let z1 = min(z0 + World.CS, World.D)

        func addQuad(x: Int, y: Int, z: Int, face: FaceDef, material: Int) {
            let start = positions.count

            positions.append(contentsOf: face.vertices)
            normals.append(contentsOf: [face.normal, face.normal, face.normal, face.normal])
            uv.append(contentsOf: [
                SCNVector2(0, 0),
                SCNVector2(1, 0),
                SCNVector2(1, 1),
                SCNVector2(0, 1)
            ])

            indicesByMaterial[material].append(contentsOf: [
                start, start + 1, start + 2,
                start + 2, start + 3, start
            ])
        }

        for x in x0..<x1 {
            for z in z0..<z1 {
                for y in 0..<World.H {
                    let b = world.get(x, y, z)
                    guard b != .air else { continue }

                    let mi = materialIndex(for: b)

                    if world.faceVisible(current: b, neighbor: world.get(x, y + 1, z)) {
                        addQuad(
                            x: x, y: y, z: z,
                            face: FaceDef(
                                vertices: [
                                    SCNVector3(Float(x), Float(y + 1), Float(z)),
                                    SCNVector3(Float(x + 1), Float(y + 1), Float(z)),
                                    SCNVector3(Float(x + 1), Float(y + 1), Float(z + 1)),
                                    SCNVector3(Float(x), Float(y + 1), Float(z + 1))
                                ],
                                normal: SCNVector3(0, 1, 0)
                            ),
                            material: mi
                        )
                    }

                    if world.faceVisible(current: b, neighbor: world.get(x, y - 1, z)) {
                        addQuad(
                            x: x, y: y, z: z,
                            face: FaceDef(
                                vertices: [
                                    SCNVector3(Float(x), Float(y), Float(z)),
                                    SCNVector3(Float(x), Float(y), Float(z + 1)),
                                    SCNVector3(Float(x + 1), Float(y), Float(z + 1)),
                                    SCNVector3(Float(x + 1), Float(y), Float(z))
                                ],
                                normal: SCNVector3(0, -1, 0)
                            ),
                            material: mi
                        )
                    }

                    if world.faceVisible(current: b, neighbor: world.get(x + 1, y, z)) {
                        addQuad(
                            x: x, y: y, z: z,
                            face: FaceDef(
                                vertices: [
                                    SCNVector3(Float(x + 1), Float(y), Float(z)),
                                    SCNVector3(Float(x + 1), Float(y), Float(z + 1)),
                                    SCNVector3(Float(x + 1), Float(y + 1), Float(z + 1)),
                                    SCNVector3(Float(x + 1), Float(y + 1), Float(z))
                                ],
                                normal: SCNVector3(1, 0, 0)
                            ),
                            material: mi
                        )
                    }

                    if world.faceVisible(current: b, neighbor: world.get(x - 1, y, z)) {
                        addQuad(
                            x: x, y: y, z: z,
                            face: FaceDef(
                                vertices: [
                                    SCNVector3(Float(x), Float(y), Float(z)),
                                    SCNVector3(Float(x), Float(y), Float(z + 1)),
                                    SCNVector3(Float(x), Float(y + 1), Float(z + 1)),
                                    SCNVector3(Float(x), Float(y + 1), Float(z))
                                ],
                                normal: SCNVector3(-1, 0, 0)
                            ),
                            material: mi
                        )
                    }

                    if world.faceVisible(current: b, neighbor: world.get(x, y, z + 1)) {
                        addQuad(
                            x: x, y: y, z: z,
                            face: FaceDef(
                                vertices: [
                                    SCNVector3(Float(x + 1), Float(y), Float(z + 1)),
                                    SCNVector3(Float(x), Float(y), Float(z + 1)),
                                    SCNVector3(Float(x), Float(y + 1), Float(z + 1)),
                                    SCNVector3(Float(x + 1), Float(y + 1), Float(z + 1))
                                ],
                                normal: SCNVector3(0, 0, 1)
                            ),
                            material: mi
                        )
                    }

                    if world.faceVisible(current: b, neighbor: world.get(x, y, z - 1)) {
                        addQuad(
                            x: x, y: y, z: z,
                            face: FaceDef(
                                vertices: [
                                    SCNVector3(Float(x), Float(y), Float(z)),
                                    SCNVector3(Float(x + 1), Float(y), Float(z)),
                                    SCNVector3(Float(x + 1), Float(y + 1), Float(z)),
                                    SCNVector3(Float(x), Float(y + 1), Float(z))
                                ],
                                normal: SCNVector3(0, 0, -1)
                            ),
                            material: mi
                        )
                    }
                }
            }
        }

        guard !positions.isEmpty else {
            return SCNNode()
        }

        let vSource = SCNGeometrySource(vertices: positions)
        let nSource = SCNGeometrySource(normals: normals)
        let tSource = SCNGeometrySource(textureCoordinates: uv)

        var elements: [SCNGeometryElement] = []

        for (i, idx) in indicesByMaterial.enumerated() where !idx.isEmpty {
            let int32 = idx.map { Int32($0) }
            let data = Data(
                bytes: int32,
                count: int32.count * MemoryLayout<Int32>.size
            )

            let element = SCNGeometryElement(
                data: data,
                primitiveType: .triangles,
                primitiveCount: idx.count / 3,
                bytesPerIndex: MemoryLayout<Int32>.size
            )
            element.materialIndex = i
            elements.append(element)
        }

        let geometry = SCNGeometry(
            sources: [vSource, nSource, tSource],
            elements: elements
        )

        geometry.frontFacingWinding = .clockwise
        geometry.materials = materials

        let node = SCNNode(geometry: geometry)
        node.castsShadow = true
        node.name = "chunk_\(cx)_\(cz)"
        return node
    }
}

// MARK: - Materials

final class MaterialFactory {
    static func makeMaterials() -> [SCNMaterial] {
        let grassTex = texture(
            base: UIColor(red: 0.31, green: 0.65, blue: 0.30, alpha: 1),
            accent: UIColor(red: 0.24, green: 0.54, blue: 0.24, alpha: 1),
            dark: UIColor(red: 0.18, green: 0.42, blue: 0.18, alpha: 1),
            seed: 101
        )

        let dirtTex = texture(
            base: UIColor(red: 0.42, green: 0.29, blue: 0.18, alpha: 1),
            accent: UIColor(red: 0.32, green: 0.22, blue: 0.14, alpha: 1),
            dark: UIColor(red: 0.22, green: 0.15, blue: 0.10, alpha: 1),
            seed: 102
        )

        let stoneTex = texture(
            base: UIColor(red: 0.54, green: 0.56, blue: 0.60, alpha: 1),
            accent: UIColor(red: 0.42, green: 0.44, blue: 0.48, alpha: 1),
            dark: UIColor(red: 0.32, green: 0.34, blue: 0.38, alpha: 1),
            seed: 103
        )

        let woodTex = texture(
            base: UIColor(red: 0.35, green: 0.23, blue: 0.15, alpha: 1),
            accent: UIColor(red: 0.26, green: 0.17, blue: 0.11, alpha: 1),
            dark: UIColor(red: 0.18, green: 0.12, blue: 0.08, alpha: 1),
            seed: 104,
            verticalLines: true
        )

        let leavesTex = texture(
            base: UIColor(red: 0.18, green: 0.48, blue: 0.21, alpha: 1),
            accent: UIColor(red: 0.14, green: 0.38, blue: 0.17, alpha: 1),
            dark: UIColor(red: 0.09, green: 0.27, blue: 0.12, alpha: 1),
            seed: 105
        )

        let sandTex = texture(
            base: UIColor(red: 0.86, green: 0.80, blue: 0.58, alpha: 1),
            accent: UIColor(red: 0.76, green: 0.70, blue: 0.50, alpha: 1),
            dark: UIColor(red: 0.65, green: 0.58, blue: 0.42, alpha: 1),
            seed: 106
        )

        let glassTex = texture(
            base: UIColor.white,
            accent: UIColor.white,
            dark: UIColor.white,
            seed: 107,
            glass: true
        )

        let brickTex = texture(
            base: UIColor(red: 0.68, green: 0.28, blue: 0.22, alpha: 1),
            accent: UIColor(red: 0.54, green: 0.22, blue: 0.18, alpha: 1),
            dark: UIColor(red: 0.82, green: 0.80, blue: 0.75, alpha: 1),
            seed: 108,
            brick: true
        )

        let mats: [SCNMaterial] = [
            makeMaterial(diffuse: grassTex),
            makeMaterial(diffuse: dirtTex),
            makeMaterial(diffuse: stoneTex),
            makeMaterial(diffuse: woodTex),
            makeMaterial(diffuse: leavesTex),
            makeMaterial(diffuse: sandTex),
            makeMaterial(diffuse: glassTex, transparent: true),
            makeMaterial(diffuse: brickTex)
        ]

        return mats
    }

    static func makeMaterial(diffuse: UIImage, transparent: Bool = false) -> SCNMaterial {
        let material = SCNMaterial()
        material.lightingModel = .blinn
        material.diffuse.contents = diffuse
        material.diffuse.mipFilter = .linear
        material.diffuse.wrapS = .repeat
        material.diffuse.wrapT = .repeat
        material.isDoubleSided = true

        if transparent {
            material.transparency = 0.35
            material.writesToDepthBuffer = true
            material.blendMode = .alpha
            material.transparencyMode = .dualSide
        }

        return material
    }

    static func texture(
        base: UIColor,
        accent: UIColor,
        dark: UIColor,
        seed: UInt32,
        verticalLines: Bool = false,
        glass: Bool = false,
        brick: Bool = false
    ) -> UIImage {
        let size = 16
        let renderer = UIGraphicsImageRenderer(size: CGSize(width: size, height: size))

        return renderer.image { ctx in
            let cg = ctx.cgContext

            cg.setFillColor(UIColor.clear.cgColor)
            cg.fill(CGRect(x: 0, y: 0, width: size, height: size))

            var state = seed == 0 ? 12345 : seed

            func rnd() -> Float {
                state = state &* 1664525 + 1013904223
                return Float((state >> 8) & 0xFFFFFF) / Float(0xFFFFFF)
            }

            for y in 0..<size {
                for x in 0..<size {
                    var color = base
                    let r = rnd()

                    if glass {
                        color = UIColor.white.withAlphaComponent(0.18)
                    } else if brick {
                        let mortarY = (y % 4 == 0)
                        let offset = (y / 4) % 2 == 0 ? 0 : 2
                        let mortarX = ((x + offset) % 4 == 0)

                        if mortarY || mortarX {
                            color = dark
                        } else {
                            color = r < 0.22 ? accent : base
                        }
                    } else if verticalLines, (x % 4 == 0) {
                        color = accent
                    } else {
                        if r < 0.18 {
                            color = accent
                        } else if r < 0.34 {
                            color = dark
                        } else if r > 0.94 {
                            color = UIColor.white.withAlphaComponent(0.22)
                        }
                    }

                    cg.setFillColor(color.cgColor)
                    cg.fill(CGRect(x: x, y: y, width: 1, height: 1))
                }
            }
        }
    }
}

// MARK: - Game Scene View

struct GameSceneView: UIViewRepresentable {
    @ObservedObject var controller: GameController

    func makeCoordinator() -> Coordinator {
        Coordinator(controller: controller)
    }

    func makeUIView(context: Context) -> SCNView {
        let view = SCNView()
        view.scene = controller.scene
        view.delegate = controller
        view.pointOfView = controller.cameraNode
        view.allowsCameraControl = false
        view.autoenablesDefaultLighting = false
        view.antialiasingMode = .multisampling4X
        view.preferredFramesPerSecond = 60
        view.backgroundColor = UIColor(red: 0.55, green: 0.78, blue: 0.95, alpha: 1)
        view.isJitteringEnabled = true
        context.coordinator.view = view
        return view
    }

    func updateUIView(_ uiView: SCNView, context: Context) {
        uiView.scene = controller.scene
        uiView.delegate = controller
        uiView.pointOfView = controller.cameraNode
    }

    final class Coordinator: NSObject {
        weak var view: SCNView?
        init(controller: GameController) {
            super.init()
        }
    }
}

// MARK: - Game Controller

final class GameController: NSObject, ObservableObject, SCNSceneRendererDelegate {
    let scene = SCNScene()
    let world = World()
    let materials = MaterialFactory.makeMaterials()

    let playerNode = SCNNode()
    let cameraNode = SCNNode()

    @Published var selectedBlock: Block = .grass
    @Published var moveVec = CGSize.zero
    @Published var yaw: Float = 0
    @Published var pitch: Float = -0.18

    var jumpRequest = false

    var pos = SCNVector3(0, 30, 0)
    var velocity = SCNVector3(0, 0, 0)
    var grounded = false
    var lastTime: TimeInterval = 0

    var chunkNodes: [Int: SCNNode] = [:]

    let playerWidth: Float = 0.34
    let playerDepth: Float = 0.34
    let playerHeight: Float = 1.75
    let eyeHeight: Float = 1.62
    let moveSpeed: Float = 5.5
    let jumpSpeed: Float = 7.2
    let gravity: Float = 21.5

    override init() {
        super.init()
        setupScene()
        generateWorld()
        spawnPlayer()
    }

    func setupScene() {
        scene.background.contents = UIColor(red: 0.55, green: 0.78, blue: 0.95, alpha: 1)

        let camera = SCNCamera()
        camera.zNear = 0.1
        camera.zFar = 200
        camera.fieldOfView = 70
        camera.wantsHDR = false
        cameraNode.camera = camera
        cameraNode.position = SCNVector3(0, eyeHeight, 0)

        let sun = SCNLight()
        sun.type = .directional
        sun.intensity = 1100
        sun.castsShadow = true
        sun.shadowMode = .modulated
        sun.shadowRadius = 5
        sun.shadowSampleCount = 8
        sun.shadowIntensity = 0.35
        let sunNode = SCNNode()
        sunNode.light = sun
        sunNode.eulerAngles = SCNVector3(-Float.pi / 3, Float.pi / 5, 0)
        scene.root.addChildNode(sunNode)

        let ambient = SCNLight()
        ambient.type = .ambient
        ambient.intensity = 420
        let ambientNode = SCNNode()
        ambientNode.light = ambient
        scene.root.addChildNode(ambientNode)

        playerNode.addChildNode(cameraNode)
        scene.root.addChildNode(playerNode)
    }

    func generateWorld() {
        world.generate()

        let cxCount = World.W / World.CS
        let czCount = World.D / World.CS

        for cz in 0..<czCount {
            for cx in 0..<cxCount {
                let node = MeshBuilder.buildChunk(
                    world: world,
                    cx: cx,
                    cz: cz,
                    materials: materials
                )
                chunkNodes[chunkKey(cx, cz)] = node
                scene.root.addChildNode(node)
            }
        }
    }

    func spawnPlayer() {
        let x = World.W / 2
        let z = World.D / 2
        let top = world.topY(x, z)

        pos = SCNVector3(
            Float(x) + 0.5,
            Float(top + 1),
            Float(z) + 0.5
        )

        playerNode.position = pos
        cameraNode.eulerAngles = SCNVector3(pitch, yaw, 0)
    }

    func chunkKey(_ cx: Int, _ cz: Int) -> Int {
        cx * 10000 + cz
    }

    func rebuildChunk(cx: Int, cz: Int) {
        let cxCount = World.W / World.CS
        let czCount = World.D / World.CS
        guard cx >= 0, cx < cxCount, cz >= 0, cz < czCount else { return }

        let key = chunkKey(cx, cz)
        if let old = chunkNodes[key] {
            old.removeFromParentNode()
            chunkNodes.removeValue(forKey: key)
        }

        let node = MeshBuilder.buildChunk(
            world: world,
            cx: cx,
            cz: cz,
            materials: materials
        )
        chunkNodes[key] = node
        scene.root.addChildNode(node)
    }

    func rebuildAround(x: Int, z: Int) {
        let cx = x / World.CS
        let cz = z / World.CS

        rebuildChunk(cx: cx, cz: cz)

        if x % World.CS == 0 {
            rebuildChunk(cx: cx - 1, cz: cz)
        }
        if x % World.CS == World.CS - 1 {
            rebuildChunk(cx: cx + 1, cz: cz)
        }
        if z % World.CS == 0 {
            rebuildChunk(cx: cx, cz: cz - 1)
        }
        if z % World.CS == World.CS - 1 {
            rebuildChunk(cx: cx, cz: cz + 1)
        }
    }

    func jump() {
        jumpRequest = true
    }

    func breakBlock() {
        guard let hit = raycast(maxDistance: 8) else { return }

        let x = Int(hit.target.x)
        let y = Int(hit.target.y)
        let z = Int(hit.target.z)

        guard y > 0 else { return }
        guard world.get(x, y, z) != .air else { return }

        world.set(x, y, z, .air)
        rebuildAround(x: x, z: z)
    }

    func placeBlock() {
        guard let hit = raycast(maxDistance: 8) else { return }

        let x = Int(hit.place.x)
        let y = Int(hit.place.y)
        let z = Int(hit.place.z)

        guard world.inBounds(x, y, z) else { return }
        guard world.get(x, y, z) == .air else { return }

        if blockIntersectsPlayer(x: x, y: y, z: z) {
            return
        }

        world.set(x, y, z, selectedBlock)
        rebuildAround(x: x, z: z)
    }

    func blockIntersectsPlayer(x: Int, y: Int, z: Int) -> Bool {
        let halfW = playerWidth * 0.5
        let halfD = playerDepth * 0.5

        let bMinX = Float(x)
        let bMaxX = Float(x + 1)
        let bMinY = Float(y)
        let bMaxY = Float(y + 1)
        let bMinZ = Float(z)
        let bMaxZ = Float(z + 1)

        let pMinX = pos.x - halfW
        let pMaxX = pos.x + halfW
        let pMinY = pos.y
        let pMaxY = pos.y + playerHeight
        let pMinZ = pos.z - halfD
        let pMaxZ = pos.z + halfD

        return pMaxX > bMinX &&
               pMinX < bMaxX &&
               pMaxY > bMinY &&
               pMinY < bMaxY &&
               pMaxZ > bMinZ &&
               pMinZ < bMaxZ
    }

    func normalized(_ v: SCNVector3) -> SCNVector3 {
        let len = max(0.0001, sqrt(v.x * v.x + v.y * v.y + v.z * v.z))
        return SCNVector3(v.x / len, v.y / len, v.z / len)
    }

    func cameraForward() -> SCNVector3 {
        let cp = cos(pitch)
        let sp = sin(pitch)
        let cy = cos(yaw)
        let sy = sin(yaw)

        return SCNVector3(
            sy * cp,
            sp,
            -cy * cp
        )
    }

    func raycast(maxDistance: Float) -> (target: SCNVector3, place: SCNVector3)? {
        let origin = SCNVector3(pos.x, pos.y + eyeHeight, pos.z)
        let dir = normalized(cameraForward())

        var x = Int(floor(origin.x))
        var y = Int(floor(origin.y))
        var z = Int(floor(origin.z))

        var prev = SCNVector3(Float(x), Float(y), Float(z))

        let stepX = dir.x >= 0 ? 1 : -1
        let stepY = dir.y >= 0 ? 1 : -1
        let stepZ = dir.z >= 0 ? 1 : -1

        let tDeltaX: Float = abs(dir.x) > 1e-6 ? 1 / abs(dir.x) : .greatestFiniteMagnitude
        let tDeltaY: Float = abs(dir.y) > 1e-6 ? 1 / abs(dir.y) : .greatestFiniteMagnitude
        let tDeltaZ: Float = abs(dir.z) > 1e-6 ? 1 / abs(dir.z) : .greatestFiniteMagnitude

        var tMaxX: Float = dir.x > 0 ? (Float(x + 1) - origin.x) / dir.x : (origin.x - Float(x)) / (-dir.x)
        var tMaxY: Float = dir.y > 0 ? (Float(y + 1) - origin.y) / dir.y : (origin.y - Float(y)) / (-dir.y)
        var tMaxZ: Float = dir.z > 0 ? (Float(z + 1) - origin.z) / dir.z : (origin.z - Float(z)) / (-dir.z)

        for _ in 0..<200 {
            if tMaxX < tMaxY && tMaxX < tMaxZ {
                prev = SCNVector3(Float(x), Float(y), Float(z))
                x += stepX
                tMaxX += tDeltaX
                if tMaxX > maxDistance { break }
            } else if tMaxY < tMaxZ {
                prev = SCNVector3(Float(x), Float(y), Float(z))
                y += stepY
                tMaxY += tDeltaY
                if tMaxY > maxDistance { break }
            } else {
                prev = SCNVector3(Float(x), Float(y), Float(z))
                z += stepZ
                tMaxZ += tDeltaZ
                if tMaxZ > maxDistance { break }
            }

            if world.isSolid(x, y, z) {
                return (
                    target: SCNVector3(Float(x), Float(y), Float(z)),
                    place: prev
                )
            }
        }

        return nil
    }

    func renderer(_ renderer: SCNSceneRenderer, updateAtTime time: TimeInterval) {
        let dt: Float
        if lastTime == 0 {
            dt = 1.0 / 60.0
        } else {
            dt = Float(min(0.05, time - lastTime))
        }
        lastTime = time

        updatePhysics(dt: dt)

        cameraNode.eulerAngles = SCNVector3(pitch, yaw, 0)
    }

    func updatePhysics(dt: Float) {
        let f = SCNVector3(sin(yaw), 0, -cos(yaw))
        let r = SCNVector3(cos(yaw), 0, sin(yaw))

        let forward = moveVec.height
        let right = moveVec.width

        var mv = SCNVector3(
            f.x * forward + r.x * right,
            0,
            f.z * forward + r.z * right
        )

        let len = sqrt(mv.x * mv.x + mv.z * mv.z)
        if len > 0.001 {
            mv = SCNVector3(mv.x / len, 0, mv.z / len)
            velocity.x = mv.x * moveSpeed
            velocity.z = mv.z * moveSpeed
        } else {
            velocity.x = 0
            velocity.z = 0
        }

        velocity.y -= gravity * dt

        if jumpRequest && grounded {
            velocity.y = jumpSpeed
            jumpRequest = false
        }

        moveX(velocity.x * dt)
        moveY(velocity.y * dt)
        moveZ(velocity.z * dt)

        playerNode.position = pos
    }

    func moveX(_ dx: Float) {
        guard abs(dx) > 1e-6 else { return }

        let nx = pos.x + dx
        let half = playerWidth * 0.5

        let minY = Int(floor(pos.y + 0.001))
        let maxY = Int(ceil(pos.y + playerHeight - 0.001) - 1)
        let zMin = Int(floor(pos.z - half))
        let zMax = Int(floor(pos.z + half))

        if dx > 0 {
            let bx = Int(floor(nx + half))
            for y in minY...maxY {
                for z in zMin...zMax {
                    if world.isSolid(bx, y, z) {
                        pos.x = Float(bx) - half - 0.001
                        velocity.x = 0
                        return
                    }
                }
            }
        } else {
            let bx = Int(floor(nx - half))
            for y in minY...maxY {
                for z in zMin...zMax {
                    if world.isSolid(bx, y, z) {
                        pos.x = Float(bx) + 1 + half + 0.001
                        velocity.x = 0
                        return
                    }
                }
            }
        }

        pos.x = nx
    }

    func moveY(_ dy: Float) {
        grounded = false

        let halfW = playerWidth * 0.5
        let halfD = playerDepth * 0.5
        let xMin = Int(floor(pos.x - halfW))
        let xMax = Int(floor(pos.x + halfW))
        let zMin = Int(floor(pos.z - halfD))
        let zMax = Int(floor(pos.z + halfD))

        if dy < 0 {
            let ny = pos.y + dy
            let by = Int(floor(ny))

            for x in xMin...xMax {
                for z in zMin...zMax {
                    if world.isSolid(x, by, z) {
                        pos.y = Float(by) + 1 + 0.001
                        velocity.y = 0
                        grounded = true
                        return
                    }
                }
            }

            pos.y = ny
            if pos.y <= 0 {
                pos.y = 0
                velocity.y = 0
                grounded = true
            }
        } else {
            let ny = pos.y + playerHeight + dy
            let by = Int(floor(ny - 0.001))

            for x in xMin...xMax {
                for z in zMin...zMax {
                    if world.isSolid(x, by, z) {
                        pos.y = Float(by) - playerHeight - 0.001
                        velocity.y = 0
                        return
                    }
                }
            }

            pos.y += dy
        }

        checkGround()
    }

    func moveZ(_ dz: Float) {
        guard abs(dz) > 1e-6 else { return }

        let nz = pos.z + dz
        let half = playerDepth * 0.5

        let minY = Int(floor(pos.y + 0.001))
        let maxY = Int(ceil(pos.y + playerHeight - 0.001) - 1)
        let xMin = Int(floor(pos.x - half))
        let xMax = Int(floor(pos.x + half))

        if dz > 0 {
            let bz = Int(floor(nz + half))
            for y in minY...maxY {
                for x in xMin...xMax {
                    if world.isSolid(x, y, bz) {
                        pos.z = Float(bz) - half - 0.001
                        velocity.z = 0
                        return
                    }
                }
            }
        } else {
            let bz = Int(floor(nz - half))
            for y in minY...maxY {
                for x in xMin...xMax {
                    if world.isSolid(x, y, bz) {
                        pos.z = Float(bz) + 1 + half + 0.001
                        velocity.z = 0
                        return
                    }
                }
            }
        }

        pos.z = nz
    }

    func checkGround() {
        let halfW = playerWidth * 0.5
        let halfD = playerDepth * 0.5
        let by = Int(floor(pos.y - 0.001))

        let xMin = Int(floor(pos.x - halfW))
        let xMax = Int(floor(pos.x + halfW))
        let zMin = Int(floor(pos.z - halfD))
        let zMax = Int(floor(pos.z + halfD))

        for x in xMin...xMax {
            for z in zMin...zMax {
                if world.isSolid(x, by, z) {
                    grounded = true
                    return
                }
            }
        }
    }
}

// MARK: - UI

struct JoystickView: View {
    @ObservedObject var controller: GameController

    @State private var thumb = CGSize.zero

    var body: some View {
        ZStack {
            Circle()
                .fill(.white.opacity(0.12))
                .frame(width: 115, height: 115)
                .overlay(
                    Circle()
                        .stroke(.white.opacity(0.55), lineWidth: 1.5)
                )

            Circle()
                .fill(.white.opacity(0.48))
                .frame(width: 46, height: 46)
                .offset(thumb)
        }
        .frame(width: 125, height: 125)
        .contentShape(Circle())
        .gesture(
            DragGesture(minimumDistance: 0)
                .onChanged { value in
                    let dx = value.translation.width / 55
                    let dy = value.translation.height / 55

                    let raw = CGSize(width: dx, height: dy)
                    let len = sqrt(raw.width * raw.width + raw.height * raw.height)

                    let clamped: CGSize
                    if len > 1 {
                        clamped = CGSize(width: raw.width / len, height: raw.height / len)
                    } else {
                        clamped = raw
                    }

                    thumb = CGSize(width: clamped.width * 38, height: clamped.height * 38)
                    controller.moveVec = CGSize(width: clamped.width, height: -clamped.height)
                }
                .onEnded { _ in
                    thumb = .zero
                    controller.moveVec = .zero
                }
        )
    }
}

struct ActionButtonsView: View {
    @ObservedObject var controller: GameController
    @State private var rotationLast = CGSize.zero

    var body: some View {
        HStack(alignment: .bottom, spacing: 12) {
            Color.clear
                .frame(width: 135, height: 190)
                .contentShape(Rectangle())
                .gesture(
                    DragGesture(minimumDistance: 0)
                        .onChanged { value in
                            let dx = value.translation.width - rotationLast.width
                            let dy = value.translation.height - rotationLast.height

                            controller.yaw += Float(dx) * 0.006
                            controller.pitch = max(
                                -1.45,
                                min(1.45, controller.pitch - Float(dy) * 0.006)
                            )

                            if abs(controller.yaw) > .pi * 2 {
                                controller.yaw = controller.yaw.truncatingRemainder(dividingBy: .pi * 2)
                            }

                            rotationLast = value.translation
                        }
                        .onEnded { _ in
                            rotationLast = .zero
                        }
                )

            VStack(spacing: 10) {
                GameButton(title: "PLACE") {
                    controller.placeBlock()
                }
                .foregroundColor(.green)

                GameButton(title: "BREAK") {
                    controller.breakBlock()
                }
                .foregroundColor(.red)

                GameButton(title: "JUMP") {
                    controller.jump()
                }
                .foregroundColor(.blue)
            }
        }
    }
}

struct GameButton: View {
    let title: String
    let action: () -> Void
    var color: Color = .white

    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.system(size: 15, weight: .bold, design: .rounded))
                .foregroundColor(color)
                .padding(.horizontal, 16)
                .padding(.vertical, 12)
                .background(.black.opacity(0.25), in: RoundedRectangle(cornerRadius: 12))
                .overlay(
                    RoundedRectangle(cornerRadius: 12)
                        .stroke(color.opacity(0.6), lineWidth: 1)
                )
        }
        .buttonStyle(.plain)
    }
}

extension GameButton {
    func foregroundColor(_ color: Color) -> GameButton {
        var copy = self
        copy.color = color
        return copy
    }
}

struct HotbarView: View {
    @ObservedObject var controller: GameController

    var blocks: [Block] {
        Block.allCases.filter { $0 != .air }
    }

    var body: some View {
        HStack(spacing: 8) {
            ForEach(blocks) { block in
                Button {
                    controller.selectedBlock = block
                } label: {
                    ZStack {
                        RoundedRectangle(cornerRadius: 9)
                            .fill(block.color.opacity(0.92))

                        Text(block.emoji)
                            .font(.system(size: 20))
                    }
                    .frame(width: 46, height: 46)
                    .overlay(
                        RoundedRectangle(cornerRadius: 9)
                            .stroke(
                                controller.selectedBlock == block ? Color.white : Color.white.opacity(0.35),
                                lineWidth: controller.selectedBlock == block ? 3 : 1
                            )
                    )
                    .scaleEffect(controller.selectedBlock == block ? 1.08 : 1.0)
                    .animation(.easeOut(duration: 0.12), value: controller.selectedBlock)
                }
                .buttonStyle(.plain)
            }
        }
        .padding(.horizontal, 10)
        .padding(.vertical, 8)
        .background(.black.opacity(0.22), in: RoundedRectangle(cornerRadius: 14))
    }
}

作れます。  
Swift（iOS / SwiftUI + SceneKit）で、**マイクラ風の 3D 箱庭ブロックゲーム**を 1 ファイルで作れる形にまとめます。

そのまま Xcode に貼れる Swift コードです。  
機能は簡易版ですが、以下が入っています。

- 3D 視点は一人称
- 画面スティックで移動
- 画面をドラッグで視点操作
- タップでブロック破壊
- 設置モードに切り替えてブロック設置
- ジャンプ
- 草・土・石・木・砂・葉の複数ブロック
- 自動生成した地形に木あり

---

## 手順

1. Xcode で新規プロジェクト作成  
   - File > New Project > iOS App  
   - Interface: SwiftUI
2. `ContentView.swift` を下記コードで全部置き換え
3. 実機シミュレーターで起動
4. スティックで移動、画面ドラッグで視点、タップで破壊/設置

※ iOS 16 以上推奨。  
※ 完全に「Minecraft」そのものではなく、あくまで 3D 箱庭ブロックゲーム風です。

---

```swift
import SwiftUI
import SceneKit

// MARK: - Grid Position

struct GridPos: Hashable {
    var x: Int
    var y: Int
    var z: Int

    init(_ x: Int, _ y: Int, _ z: Int) {
        self.x = x
        self.y = y
        self.z = z
    }

    init?(name: String?) {
        guard let name = name else { return nil }
        let parts = name.split(separator: ",")
        guard parts.count == 3,
              let xi = Int(parts[0]),
              let yi = Int(parts[1]),
              let zi = Int(parts[2]) else { return nil }
        self.init(xi, yi, zi)
    }
}

// MARK: - Block Types

enum BlockType: CaseIterable, Hashable {
    case grass
    case dirt
    case stone
    case wood
    case sand
    case leaf

    var name: String {
        switch self {
        case .grass: return "草"
        case .dirt:  return "土"
        case .stone: return "石"
        case .wood:  return "木"
        case .sand:  return "砂"
        case .leaf:  return "葉"
        }
    }

    var uiColor: UIColor {
        switch self {
        case .grass: return UIColor(red: 0.42, green: 0.78, blue: 0.36, alpha: 1)
        case .dirt:  return UIColor(red: 0.55, green: 0.38, blue: 0.23, alpha: 1)
        case .stone: return UIColor(red: 0.58, green: 0.58, blue: 0.58, alpha: 1)
        case .wood:  return UIColor(red: 0.45, green: 0.29, blue: 0.16, alpha: 1)
        case .sand:  return UIColor(red: 0.92, green: 0.86, blue: 0.62, alpha: 1)
        case .leaf:  return UIColor(red: 0.28, green: 0.65, blue: 0.22, alpha: 1)
        }
    }

    var swiftColor: Color {
        switch self {
        case .grass: return Color(red: 0.42, green: 0.78, blue: 0.36)
        case .dirt:  return Color(red: 0.55, green: 0.38, blue: 0.23)
        case .stone: return Color(red: 0.58, green: 0.58, blue: 0.58)
        case .wood:  return Color(red: 0.45, green: 0.29, blue: 0.16)
        case .sand:  return Color(red: 0.92, green: 0.86, blue: 0.62)
        case .leaf:  return Color(red: 0.28, green: 0.65, blue: 0.22)
        }
    }
}

// MARK: - Math Helpers

private func transformed(_ v: SCNVector3, _ m: SCNMatrix4) -> SCNVector3 {
    return SCNVector3(
        m.m11 * v.x + m.m12 * v.y + m.m13 * z,
        m.m21 * v.x + m.m22 * v.y + m.m23 * v.z,
        m.m31 * v.x + m.m32 * v.y + m.m33 * v.z
    )
}

private func normalized(_ v: SCNVector3) -> SCNVector3? {
    let mag = sqrt(v.x * v.x + v.y * v.y + v.z * v.z)
    guard mag > 0.0001 else { return nil }
    return SCNVector3(v.x / mag, v.y / mag, v.z / mag)
}

// MARK: - Game Model

final class GameModel: ObservableObject {
    @Published var selectedType: BlockType = .grass
    @Published var placingMode: Bool = false
    @Published var joyX: CGFloat = 0
    @Published var joyY: CGFloat = 0
    @Published var status = "Tap: 草 破壊"

    var yaw: Float = 0
    var pitch: Float = 0
    var feet = SCNVector3(8, 6, 8)
    var vy: Float = 0
    var onGround = false
    var jumpRequested = false

    let worldSize = 16
    let scene = SCNScene()
    let camera = SCNNode()
    var blocks: [GridPos: SCNNode] = [:]

    private var timer: Timer?
    private let cube = SCNBox(width: 1, height: 1, length: 1, chamferRadius: 0.01)

    init() {
        buildWorld()
    }

    func buildWorld() {
        scene.background.contents = UIColor(red: 0.53, green: 0.75, blue: 0.95, alpha: 1)

        scene.rootNode.addChildNode(camera)
        scene.camera = camera

        camera.camera = SCNCamera()
        camera.camera?.nearZ = 0.01
        camera.camera?.farZ = 120
        camera.categoryBitMask = 0

        let ambientLight = SCNLight()
        ambientLight.type = .ambient
        ambientLight.intensity = 750
        ambientLight.color = UIColor.white
        let ambientNode = SCNNode(light: ambientLight)
        ambientNode.categoryBitMask = 0
        scene.rootNode.addChildNode(ambientNode)

        let sun = SCNLight()
        sun.type = .directional
        sun.intensity = 850
        let sunNode = SCNNode(light: sun)
        sunNode.categoryBitMask = 0
        sunNode.eulerAngles = SCNVector3(-Float.pi / 3, Float.pi / 4, 0)
        scene.rootNode.addChildNode(sunNode)

        generateTerrain()

        feet = SCNVector3(8, 6, 8)
        yaw = 0
        pitch = 0
        vy = 0
        onGround = false
    }

    func generateTerrain() {
        removeAllBlocks()

        for x in 0..<worldSize {
            for z in 0..<worldSize {
                let h = Int((sin(Float(x) * 0.35) + cos(Float(z) * 0.35) + 1.6).rounded())
                let top = max(0, min(3, h))

                for y in 0...top {
                    let type: BlockType
                    if y == top {
                        type = .grass
                    } else if y == top - 1 {
                        type = .dirt
                    } else {
                        type = .stone
                    }
                    addBlock(GridPos(x, y, z), type: type)
                }
            }
        }

        addTree(at: 4, z: 4)
        addTree(at: 11, z: 9)
        addTree(at: 8, z: 12)
    }

    func removeAllBlocks() {
        for (_, node) in blocks {
            node.removeFromParentNode()
        }
        blocks.removeAll()
    }

    func addTree(at x: Int, z: Int) {
        let h = Int((sin(Float(x) * 0.35) + cos(Float(z) * 0.35) + 1.6).rounded())
        let top = max(0, min(3, h))

        for y in (top + 1)...(top + 3) {
            addBlock(GridPos(x, y, z), type: .wood)
        }

        for dx in -1...1 {
            for dz in -1...1 {
                for dy in (top + 4)...(top + 5) {
                    addBlock(GridPos(x + dx, dy, z + dz), type: .leaf)
                }
            }
        }
    }

    func addBlock(_ pos: GridPos, type: BlockType) {
        guard pos.x >= 0, pos.x < worldSize,
              pos.y >= 0, pos.y < 32,
              pos.z >= 0, pos.z < worldSize else { return }

        if blocks[pos] != nil { return }

        let node = SCNNode(geometry: cube)
        node.position = SCNVector3(Float(pos.x), Float(pos.y), Float(pos.z))
        node.name = "\(pos.x),\(pos.y),\(pos.z)"
        node.categoryBitMask = 1

        let material = SCNMaterial()
        material.diffuse.contents = type.uiColor
        material.lightingModel = .physicallyBased
        material.metal.contents = 0.0
        material.roughness.contents = 0.85
        node.materials = [material]

        scene.rootNode.addChildNode(node)
        blocks[pos] = node
    }

    func start() {
        timer?.invalidate()
        timer = Timer.scheduledTimer(withTimeInterval: 1.0 / 60.0, repeats: true) { [weak self] _ in
            self?.update(1.0 / 60.0)
        }
    }

    func stop() {
        timer?.invalidate()
        timer = nil
    }

    func update(_ dt: Float) {
        camera.position = SCNVector3(feet.x, feet.y + 1.7, feet.z)
        camera.eulerAngles = SCNVector3(pitch, yaw, 0)

        if jumpRequested {
            jumpRequested = false
            if onGround {
                vy = 8.6
                onGround = false
            }
        }

        let forward = transformed(SCNVector3(0, 0, -1), camera.worldTransform)
        let right = transformed(SCNVector3(1, 0, 0), camera.worldTransform)

        let flatForward = normalized(SCNVector3(forward.x, 0, forward.z))
        let flatRight = normalized(SCNVector3(right.x, 0, right.z))

        var mx: Float = 0
        var mz: Float = 0

        if let f = flatForward {
            mx += f.x * Float(joyY)
            mz += f.z * Float(joyY)
        }

        if let r = flatRight {
            mx += r.x * Float(joyX)
            mz += r.z * Float(joyX)
        }

        let mag = sqrt(mx * mx + mz * mz)
        if mag > 1 {
            mx /= mag
            mz /= mag
        }

        let speed: Float = 5.5
        let desiredX = feet.x + mx * speed * dt
        let desiredZ = feet.z + mz * speed * dt

        let bodyY = Int(round(feet.y + 0.3))

        let testX = Int(round(desiredX))
        let testZCurrent = Int(round(feet.z))
        if blocks[GridPos(testX, bodyY, testZCurrent)] == nil {
            feet.x = desiredX
        }

        let testXCurrent = Int(round(feet.x))
        let testZ = Int(round(desiredZ))
        if blocks[GridPos(testXCurrent, bodyY, testZ)] == nil {
            feet.z = desiredZ
        }

        vy -= 20 * dt
        feet.y += vy * dt

        var landed = false
        let groundY = Int(round(feet.y - 0.5))
        let bx = Int(round(feet.x))
        let bz = Int(round(feet.z))

        if blocks[GridPos(bx, groundY, bz)] != nil {
            let top = Float(groundY) + 0.5
            if feet.y <= top + 0.06 && feet.y >= top - 0.65 {
                feet.y = top
                vy = 0
                landed = true
            }
        }

        onGround = landed

        if feet.y < -8 {
            feet = SCNVector3(Float(worldSize) / 2, 6, Float(worldSize) / 2)
            vy = 0
            onGround = false
        }

        status = placingMode
            ? "Tap: \(selectedType.name) 設置"
            : "Tap: \(selectedType.name) 破壊"
    }

    func handlePan(translation: CGPoint) {
        yaw += Float(translation.x) * 0.006
        pitch -= Float(translation.y) * 0.006
        pitch = max(-1.15, min(1.15, pitch))
    }

    func handleTap(location: CGPoint, view: SCNView) {
        let options: [SCNHitTestOption: Any] = [
            .searchMode: SCNHitTestSearchMode.all.rawValue,
            .boundingBoxOnly: false,
            .categoryBitMask: 1,
            .ignoreHiddenNodes: true
        ]

        let hits = view.hitTest(location, options: options)
        guard let hit = hits.first else { return }

        if placingMode {
            place(from: hit)
        } else {
            breakBlock(from: hit)
        }
    }

    private func breakBlock(from hit: SCNHitTestResult) {
        guard let node = hit.node,
              let pos = GridPos(name: node.name) else { return }

        blocks.removeValue(forKey: pos)
        node.removeFromParentNode()
    }

    private func place(from hit: SCNHitTestResult) {
        guard let node = hit.node,
              let pos = GridPos(name: node.name) else { return }

        let normal = hit.normal

        let nx = Int(round(Float(pos.x) + normal.x))
        let ny = Int(round(Float(pos.y) + normal.y))
        let nz = Int(round(Float(pos.z) + normal.z))

        let target = GridPos(nx, ny, nz)

        guard target != pos else { return }
        guard blocks[target] == nil else { return }

        addBlock(target, type: selectedType)
    }

    func reset() {
        removeAllBlocks()
        generateTerrain()
        feet = SCNVector3(8, 6, 8)
        yaw = 0
        pitch = 0
        vy = 0
        onGround = false
    }
}

// MARK: - SceneKit Container

struct SceneContainer: UIViewRepresentable {
    @ObservedObject var game: GameModel

    func makeCoordinator() -> Coordinator {
        Coordinator(game: game)
    }

    func makeUIView(context: Context) -> SCNView {
        let view = SCNView()
        view.scene = game.scene
        view.pointOfView = game.camera
        view.allowsCameraControl = false
        view.autoenablesDefaultLighting = false
        view.antialiasingMode = .multisampling4X

        let tap = UITapGestureRecognizer(
            target: context.coordinator,
            action: #selector(Coordinator.tap(_:))
        )
        tap.delegate = context.coordinator

        let pan = UIPanGestureRecognizer(
            target: context.coordinator,
            action: #selector(Coordinator.pan(_:))
        )
        pan.delegate = context.coordinator

        view.addGestureRecognizer(tap)
        view.addGestureRecognizer(pan)

        return view
    }

    func updateUIView(_ uiView: SCNView, context: Context) {
        context.coordinator.game = game
        uiView.scene = game.scene
        uiView.pointOfView = game.camera
    }

    final class Coordinator: NSObject, UIGestureRecognizerDelegate {
        weak var game: GameModel?

        init(game: GameModel) {
            self.game = game
        }

        @objc func tap(_ recognizer: UITapGestureRecognizer) {
            guard let view = recognizer.view as? SCNView,
                  let game = game,
                  recognizer.state == .ended else { return }

            let p = recognizer.location(in: view)
            game.handleTap(location: p, view: view)
        }

        @objc func pan(_ recognizer: UIPanGestureRecognizer) {
            guard let game = game else { return }
            let translation = recognizer.translation(in: recognizer.view)
            game.handlePan(translation: translation)
            recognizer.translation = .zero
        }

        func gestureRecognizer(
            _ gestureRecognizer: UIGestureRecognizer,
            shouldRecognizeSimultaneouslyWith otherGestureRecognizer: UIGestureRecognizer
        ) -> Bool {
            return true
        }
    }
}

// MARK: - Joystick

struct Joystick: View {
    @Binding var x: CGFloat
    @Binding var y: CGFloat
    @State private var offset: CGSize = .zero

    var body: some View {
        ZStack {
            Circle()
                .fill(Color.white.opacity(0.22))
                .frame(width: 140, height: 140)
                .overlay(
                    Circle()
                        .stroke(Color.white.opacity(0.55), lineWidth: 2)
                )

            Circle()
                .fill(Color.white.opacity(0.75))
                .frame(width: 62, height: 62)
                .offset(offset)
        }
        .frame(width: 140, height: 140)
        .gesture(
            DragGesture(minimumDistance: 0)
                .onChanged { value in
                    let dx = min(42, max(-42, value.translation.width))
                    let dy = min(42, max(-42, value.translation.height))
                    offset = CGSize(width: dx, height: dy)
                    x = dx / 42
                    y = -dy / 42
                }
                .onEnded { _ in
                    offset = .zero
                    x = 0
                    y = 0
                }
        )
    }
}

// MARK: - Main View

struct ContentView: View {
    @StateObject private var game = GameModel()

    var body: some View {
        ZStack {
            SceneContainer(game: game)
                .ignoresSafeArea()

            VStack(spacing: 12) {
                HStack {
                    Text(game.status)
                        .foregroundColor(.white)
                        .padding(12)
                        .background(Capsule().fill(Color.black.opacity(0.45)))
                    Spacer()
                }
                .padding(.horizontal)

                HStack(spacing: 8) {
                    ForEach(BlockType.allCases, id: \.self) { type in
                        Button {
                            game.selectedType = type
                            game.status = game.placingMode
                                ? "Tap: \(type.name) 設置"
                                : "Tap: \(type.name) 破壊"
                        } label: {
                            RoundedRectangle(cornerRadius: 8)
                                .fill(type.swiftColor)
                                .frame(width: 38, height: 38)
                                .overlay(
                                    RoundedRectangle(cornerRadius: 8)
                                        .stroke(Color.white, lineWidth: game.selectedType == type ? 2 : 0)
                                )
                        }
                        .buttonStyle(.plain)
                    }
                }
                .padding(.horizontal)

                Spacer()

                HStack(alignment: .bottom) {
                    Joystick(
                        x: Binding(
                            get: { game.joyX },
                            set: { game.joyX = $0 }
                        ),
                        y: Binding(
                            get: { game.joyY },
                            set: { game.joyY = $0 }
                        )
                    )

                    Spacer()

                    VStack(spacing: 10) {
                        Button {
                            game.jumpRequested = true
                        } label: {
                            Image(systemName: "arrow.up.circle.fill")
                                .font(.system(size: 34))
                                .foregroundColor(.white)
                                .padding(12)
                                .background(Circle().fill(Color.black.opacity(0.45)))
                        }
                        .buttonStyle(.plain)

                        Button {
                            game.placingMode.toggle()
                            game.status = game.placingMode
                                ? "Tap: \(game.selectedType.name) 設置"
                                : "Tap: \(game.selectedType.name) 破壊"
                        } label: {
                            Text(game.placingMode ? "設置 ON" : "破壊 ON")
                                .foregroundColor(.white)
                                .padding(.horizontal, 14)
                                .padding(.vertical, 10)
                                .background(Capsule().fill(Color.black.opacity(0.45)))
                        }
                        .buttonStyle(.plain)

                        Button {
                            game.reset()
                        } label: {
                            Text("Reset")
                                .foregroundColor(.white)
                                .padding(.horizontal, 14)
                                .padding(.vertical, 10)
                                .background(Capsule().fill(Color.black.opacity(0.45)))
                        }
                        .buttonStyle(.plain)
                    }
                }
                .padding()
            }
        }
        .onAppear {
            game.start()
        }
        .onDisappear {
            game.stop()
        }
    }
}

#Preview {
    ContentView()
}
```

---

## 操作

- 左下スティック：移動
- 画面ドラッグ：視点
- ブロックタップ：通常は破壊
- 「破壊 ON」を「設置 ON」にするとタップで設置
- ジャンプボタン：ジャンプ
- Reset：地形を再生成

---

## 簡易版にしている理由

完全に本家のような機能をすべて Swift 1 ファイルに入れると、  
かなり長くなります。

たとえば以下は追加拡張になります。

- クラフト
- インベントリ
- スライス生成
- 巨大ワールド
- 保存
- マルチ
- 影
- 音
- アセット読み込み
- 完全物理

まずはこのコードで  
「3D ブロック世界を歩いて、壊して、置く」  
という核のゲーム性を体験できる形にしています。
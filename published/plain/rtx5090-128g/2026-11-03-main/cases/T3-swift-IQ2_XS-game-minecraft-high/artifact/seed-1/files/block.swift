import Foundation
import AppKit
import SceneKit

// -----------------------------
// GameView: mouse/key events
// -----------------------------
final class GameView: SCNView {
    var game: Game?

    override func mouseDown(with event: NSEvent) {
        if event.button == 1 {
            game?.leftClick()
        } else if event.button == 3 {
            game?.rightClick()
        }
        game?.beginDrag(event)
    }

    override func mouseDragged(with event: NSEvent) {
        game?.drag(event)
    }

    override func mouseUp(with event: NSEvent) {
        game?.endDrag(event)
    }

    override func keyDown(with event: NSEvent) {
        game?.keyDown(event)
    }

    override func keyUp(with event: NSEvent) {
        game?.keyUp(event)
    }
}

// -----------------------------
// Game logic
// -----------------------------
final class Game: NSObject, NSApplicationDelegate, SCNViewDelegate {

    let scene = SCNScene()
    let cameraNode = SCNNode()
    let camera = SCNCamera()

    var scnView: GameView?

    var blockNodes: [Int: SCNNode] = [:]
    var blockMaterials: [Int: SCNMaterial] = [:]

    // player
    var px: Float = 32
    var py: Float = 15
    var pz: Float = 32

    var yaw: Float = 0
    var pitch: Float = 0
    var vy: Float = 0
    var onGround = false
    var fly = false
    var selectedBlock = 1

    var lastTime: TimeInterval = -1

    // input
    var keyDown = [Int: Bool]()
    var dragging = false
    var lastX: CGFloat = 0
    var lastY: CGFloat = 0

    // world config
    let size = 64
    let maxHeight = 40
    let reach: Float = 6.0

    let blockNames = [
        "草", "土", "石", "木", "葉", "砂", "板", "石畳", "光石"
    ]

    let highlightNode = SCNNode()
    let crosshairNode = SCNNode()
    let hudNode = SCNNode()

    override init() {
        super.init()
        makeMaterials()
        setupScene()
        generateWorld()
        resetPlayer()
    }

    // -----------------------------
    // App lifecycle
    // -----------------------------
    func applicationDidFinishLaunching(_ notification: Notification) {
        let window = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 1280, height: 800),
            styleMask: [.titled, .closable, .miniaturizable, .resizable],
            backing: .buffered,
            defer: false
        )

        window.title = "Minecraft-like 3D Sandbox"
        window.center()

        let view = GameView()
        view.game = self
        view.scene = scene
        view.delegate = self
        view.rendersContinuously = true
        view.antialiasingMode = .multisampling4X
        view.preferredFramesPerSecond = 60

        window.contentView = view
        window.makeFirstResponder(view)
        window.acceptsMouseMovedEvents = true
        window.makeKeyAndOrderFront(nil)

        NSApp.activate(ignoringOtherApps: true)

        scnView = view
    }

    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
        return true
    }

    // -----------------------------
    // Scene setup
    // -----------------------------
    func setupScene() {
        scene.background.contents = NSColor(red: 0.53, green: 0.77, blue: 1.0, alpha: 1)

        camera.zFar = 300
        camera.fov = 70
        cameraNode.camera = camera
        cameraNode.isHidden = true
        cameraNode.name = "camera"
        scene.rootNode.addChildNode(cameraNode)

        // highlight box
        let hb = SCNBox(size: 1.02, size: 1.02, size: 1.02, chamferRadius: 0)
        let hm = SCNMaterial()
        hm.diffuse.contents = NSColor.white.withAlphaComponent(0.35)
        hm.shadingModel = .constant
        hb.firstMaterial = hm

        highlightNode.geometry = hb
        highlightNode.name = "highlight"
        highlightNode.isHidden = true
        highlightNode.castsShadow = false
        scene.rootNode.addChildNode(highlightNode)

        // crosshair
        let cb = SCNBox(size: 0.015, size: 0.015, size: 0.015, chamferRadius: 0)
        let cm = SCNMaterial()
        cm.diffuse.contents = NSColor.white
        cm.shadingModel = .constant
        cb.firstMaterial = cm

        crosshairNode.geometry = cb
        crosshairNode.isHidden = true
        crosshairNode.position = SCNVector3(0, 0, -1)
        cameraNode.addChildNode(crosshairNode)

        // HUD
        let hud = makeTextGeometry("選択: 草  [WASD] [左:破壊] [右:設置] [F:飛行] [1-9] [Y:再生成]")
        hudNode.geometry = hud
        hudNode.scale = SCNVector3(0.045, 0.045, 0.045)
        hudNode.position = SCNVector3(-1.65, 0.95, -1.0)
        hudNode.isHidden = true
        cameraNode.addChildNode(hudNode)
    }

    // -----------------------------
    // Materials
    // -----------------------------
    func makeMaterials() {
        blockMaterials[1] = material(0.24, 0.68, 0.14)   // grass
        blockMaterials[2] = material(0.53, 0.42, 0.31)   // dirt
        blockMaterials[3] = material(0.50, 0.50, 0.50)   // stone
        blockMaterials[4] = material(0.74, 0.58, 0.37)   // wood
        blockMaterials[5] = material(0.13, 0.43, 0.10)   // leaves
        blockMaterials[6] = material(0.88, 0.78, 0.54)   // sand
        blockMaterials[7] = material(0.62, 0.45, 0.23)   // plank
        blockMaterials[8] = material(0.33, 0.33, 0.33)   // cobblestone
        blockMaterials[9] = material(1.00, 0.75, 0.25, emissive: true) // glowstone
    }

    func material(_ r: CGFloat, _ g: CGFloat, _ b: CGFloat, emissive: Bool = false) -> SCNMaterial {
        let m = SCNMaterial()
        m.diffuse.contents = NSColor(red: r, green: g, blue: b, alpha: 1)
        m.shadingModel = .constant
        if emissive {
            m.emission.contents = NSColor(red: r, green: g, blue: b, alpha: 1)
        }
        return m
    }

    // -----------------------------
    // World generation
    // -----------------------------
    func generateWorld() {
        for x in 0..<size {
            for z in 0..<size {
                let h = terrainHeight(x, z)
                for y in 0...h {
                    var id = 3 // stone
                    if y == h {
                        id = 1
                    } else if y > h - 3 {
                        id = 2
                    }
                    addBlock(x, y, z, id)
                }
            }
        }

        addTrees()
    }

    func terrainHeight(_ x: Int, _ z: Int) -> Int {
        let xf = Float(x)
        let zf = Float(z)

        let h = 12
            + 6 * sin(xf * 0.15)
            + 5 * cos(zf * 0.12)
            + 3 * sin((xf + zf) * 0.08)

        return max(1, min(24, Int(h.rounded())))
    }

    func addTrees() {
        for x in 4..<(size - 4) {
            for z in 4..<(size - 4) {
                if Int.random(in: 0..<100) < 1 {
                    let h = terrainHeight(x, z)
                    if h < 3 { continue }
                    let trunk = Int.random(in: 3...5)

                    for y in (h + 1)...(h + trunk) {
                        addBlock(x, y, z, 4)
                    }

                    let top = h + trunk
                    if top >= maxHeight - 2 { continue }

                    for dx in -2...2 {
                        for dz in -2...2 {
                            let d2 = dx * dx + dz * dz
                            if d2 > 5 { continue }

                            let tx = x + dx
                            let tz = z + dz

                            if tx >= 0 && tx < size && tz >= 0 && tz < size {
                                addBlock(tx, top, tz, 5)
                                addBlock(tx, top + 1, tz, 5)
                                if d2 < 3 {
                                    addBlock(tx, top + 2, tz, 5)
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    // -----------------------------
    // Block management
    // -----------------------------
    func key(_ x: Int, _ y: Int, _ z: Int) -> Int {
        return x * 100000 + y * 1000 + z
    }

    func addBlock(_ x: Int, _ y: Int, _ z: Int, _ id: Int) {
        guard x >= 0, x < size, y >= 0, y < maxHeight, z >= 0, z < size else { return }

        let k = key(x, y, z)
        if blockNodes[k] != nil { return }

        let box = SCNBox(size: 1, size: 1, size: 1, chamferRadius: 0)
        box.firstMaterial = blockMaterials[id]
        box.castsShadow = false

        let node = SCNNode(geometry: box)
        node.name = "block"
        node.castsShadow = false
        node.position = SCNVector3(Float(x), Float(y), Float(z))

        blockNodes[k] = node
        scene.rootNode.addChildNode(node)
    }

    func removeBlock(_ node: SCNNode) {
        guard node.name == "block" else { return }

        let x = Int(node.position.x.rounded())
        let y = Int(node.position.y.rounded())
        let z = Int(node.position.z.rounded())

        let k = key(x, y, z)
        blockNodes.removeValue(forKey: k)
        node.removeFromParent()
    }

    // -----------------------------
    // Player / collision
    // -----------------------------
    func resetPlayer() {
        px = 32
        pz = 32
        py = Float(terrainHeight(32, 32)) + 2.1
        yaw = 0
        pitch = 0
        vy = 0
        onGround = false
        fly = false
        cameraNode.position = SCNVector3(px, py, pz)
        cameraNode.eulerAngles = SCNVector3(pitch, yaw, 0)
    }

    func collides(_ x: Float, _ y: Float, _ z: Float) -> Bool {
        let feet = y - 1.6
        let head = y + 0.2

        let minBX = Int(floor(x - 0.8))
        let maxBX = Int(ceil(x + 0.8))
        let minBZ = Int(floor(z - 0.8))
        let maxBZ = Int(ceil(z + 0.8))
        let minBY = Int(floor(feet - 0.5))
        let maxBY = Int(ceil(head + 0.5))

        for bx in minBX...maxBX {
            for by in minBY...maxBY {
                for bz in minBZ...maxBZ {
                    let k = key(bx, by, bz)
                    if blockNodes[k] != nil {
                        let X = Float(bx)
                        let Y = Float(by)
                        let Z = Float(bz)

                        if abs(x - X) < 0.8 &&
                           abs(z - Z) < 0.8 &&
                           (Y - 0.5 < head && Y + 0.5 > feet) {
                            return true
                        }
                    }
                }
            }
        }

        return false
    }

    func forwardVector() -> SCNVector3 {
        let sp = sin(pitch)
        let cp = cos(pitch)
        let sy = sin(yaw)
        let cy = cos(yaw)

        return SCNVector3(-sy * cp, sp, -cy * cp)
    }

    // -----------------------------
    // Raycast
    // -----------------------------
    func raycast() -> SCNHitTestResult? {
        let dir = forwardVector()
        let from = SCNVector3(px, py, pz)
        let to = SCNVector3(
            px + dir.x * reach,
            py + dir.y * reach,
            pz + dir.z * reach
        )

        let results = scene.hitTest(
            from: from,
            to: to,
            options: [
                SCNHitTestOption.allowPointFace: true,
                SCNHitTestOption.ignoreHiddenNodes: true
            ]
        )

        for r in results {
            if r.node.name == "block" {
                return r
            }
        }

        return nil
    }

    func neighborPos(_ center: SCNVector3, _ hit: SCNVector3) -> SCNVector3 {
        var x = Int(center.x.rounded())
        var y = Int(center.y.rounded())
        var z = Int(center.z.rounded())

        let dx = hit.x - Float(x)
        let dy = hit.y - Float(y)
        let dz = hit.z - Float(z)

        if abs(dx) >= abs(dy) && abs(dx) >= abs(dz) {
            x += dx > 0 ? 1 : -1
        } else if abs(dy) >= abs(dx) && abs(dy) >= abs(dz) {
            y += dy > 0 ? 1 : -1
        } else {
            z += dz > 0 ? 1 : -1
        }

        return SCNVector3(Float(x), Float(y), Float(z))
    }

    // -----------------------------
    // Click actions
    // -----------------------------
    func leftClick() {
        guard let hit = raycast() else { return }
        removeBlock(hit.node)
    }

    func rightClick() {
        guard let hit = raycast() else { return }

        let p = neighborPos(hit.node.position, hit.worldSpace)

        let x = Int(p.x)
        let y = Int(p.y)
        let z = Int(p.z)

        if x < 0 || y < 0 || z < 0 ||
           x >= size || y >= maxHeight || z >= size {
            return
        }

        // 設置した位置に自分が重なっている場合は禁止
        if collides(Float(x), Float(y), Float(z)) {
            return
        }

        addBlock(x, y, z, selectedBlock)
    }

    // -----------------------------
    // Input handling
    // -----------------------------
    func beginDrag(_ event: NSEvent) {
        dragging = true
        let loc = event.locationInWindow
        lastX = loc.x
        lastY = loc.y
    }

    func drag(_ event: NSEvent) {
        guard dragging else { return }

        let loc = event.locationInWindow
        let dx = Float(loc.x - lastX)
        let dy = Float(loc.y - lastY)

        yaw += dx * 0.004
        pitch += dy * 0.004
        pitch = max(-1.4, min(1.4, pitch))

        lastX = loc.x
        lastY = loc.y
    }

    func endDrag(_ event: NSEvent) {
        dragging = false
    }

    func keyDown(_ event: NSEvent) {
        keyDown[event.keyCode] = true

        let c = event.charactersIgnoringModifiers
        guard c.count == 1 else { return }

        if c == "f" {
            fly.toggle()
        }
        if c == "y" {
            resetWorld()
            return
        }

        if let n = Int(c), n >= 1, n <= 9 {
            selectedBlock = n
        }
    }

    func keyUp(_ event: NSEvent) {
        keyDown[event.keyCode] = false
    }

    func resetWorld() {
        for node in blockNodes.values {
            node.removeFromParent()
        }
        blockNodes.removeAll()
        generateWorld()
        resetPlayer()
    }

    // -----------------------------
    // Update loop
    // -----------------------------
    func renderer(_ renderer: SCNSceneRenderer, updateAtTime time: TimeInterval) {
        if lastTime < 0 {
            lastTime = time
            return
        }

        let dt = Float(min(time - lastTime, 0.05))
        lastTime = time

        updateMovement(dt)

        cameraNode.position = SCNVector3(px, py, pz)
        cameraNode.eulerAngles = SCNVector3(pitch, yaw, 0)

        let hit = raycast()
        if let h = hit {
            highlightNode.isHidden = false
            highlightNode.position = h.node.position
        } else {
            highlightNode.isHidden = true
        }

        updateHUD()
    }

    func updateMovement(_ dt: Float) {
        let sy = sin(yaw)
        let cy = cos(yaw)

        let fx = -sy
        let fz = -cy
        let rx = cy
        let rz = -sy

        var dx: Float = 0
        var dz: Float = 0

        // W = 13, A = 0, S = 1, D = 2
        if keyDown[13] ?? false {
            dx += fx; dz += fz
        }
        if keyDown[1] ?? false {
            dx -= fx; dz -= fz
        }
        if keyDown[2] ?? false {
            dx += rx; dz += rz
        }
        if keyDown[0] ?? false {
            dx -= rx; dz -= rz
        }

        let len = sqrt(dx * dx + dz * dz)
        if len > 0 {
            dx /= len
            dz /= len
        }

        let speed = fly ? 6.0 : 3.5
        let mx = dx * speed * dt
        let mz = dz * speed * dt

        if !fly {
            // Space = 49
            if (keyDown[49] ?? false) && onGround {
                vy = 6.0
                onGround = false
                keyDown[49] = false
            }

            vy -= 20.0 * dt
            vy = max(-30, min(30, vy))
        } else {
            var v: Float = 0
            if keyDown[49] ?? false { v += 6.0 }
            if keyDown[56] ?? false { v -= 6.0 } // Shift
            vy = v
        }

        // X axis collision
        if mx != 0 {
            let nx = px + mx
            if collides(nx, py, pz) {
                mx = 0
            } else {
                px = nx
            }
        }

        // Z axis collision
        if mz != 0 {
            let nz = pz + mz
            if collides(px, py, nz) {
                mz = 0
            } else {
                pz = nz
            }
        }

        // Y axis collision
        let dy = vy * dt
        if dy != 0 {
            let ny = py + dy
            if collides(px, ny, pz) {
                vy = 0
                if dy < 0 {
                    onGround = true
                }
            } else {
                py = ny
                onGround = false
            }
        }
    }

    func updateHUD() {
        let name = blockNames[selectedBlock - 1]
        let text = "選択: \(name)  [WASD]  [左:破壊]  [右:設置]  [F:飛行]  [1-9]  [Y:再生成]"
        hudNode.geometry = makeTextGeometry(text)
    }

    func makeTextGeometry(_ text: String) -> SCNText {
        let t = SCNText(string: text, extrusionDepth: 0)
        t.font = NSFont.systemFont(ofSize: 1, weight: .regular)
        t.flatness = 0
        t.firstMaterial?.diffuse.contents = NSColor.white
        t.firstMaterial?.shadingModel = .constant
        return t
    }
}

// -----------------------------
// App bootstrap
// -----------------------------
let app = NSApplication.shared
let game = Game()
app.delegate = game
app.run()

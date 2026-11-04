以下は Swift/SwiftUI + SceneKit だけで動く **マイクラ風の 3D 箱庭ゲーム**です。  
iOS アプリ用で、**ブロックを壊す/置く/飛び回る** までできます。

## 操作方法

- 画面をドラッグ → 視点回転  
- 画面をタップ → ブロック破壊  
- 画面を長押し → ブロック設置  
- 左下ジョイスティック → 移動  
- 右下の `↑` / `↓` → 高さ移動  
- 下段ホットバー → 置くブロック選択  
- `飛行` ボタン → クリエイティブ飛行切替

---

## 使い方

1. Xcode で **iOS App** を作成  
2. Swift + SwiftUI + Interface Builder を選択  
3. `ContentView.swift` を下記コードに置き換え  
4. そのまま iPhone/iPad で実行

※ 既存の `@main struct ...: App` がある場合は、その `App.swift` はそのままにして、`ContentView.swift` だけを下のコードにしてください。  
※ 1ファイル完結版が欲しい場合は末尾に `App.swift` 用の `@main` コードも載せています。

---

```swift
// ContentView.swift

import SwiftUI
import SceneKit
import UIKit
import Combine

enum BlockType: String, CaseIterable, Identifiable {
    case grass
    case dirt
    case stone
    case wood
    case leaves
    case sand
    case water
    case glass

    var id: String { rawValue }

    var displayName: String {
        switch self {
        case .grass:  return "草"
        case .dirt:   return "土"
        case .stone:  return "石"
        case .wood:   return "木"
        case .leaves: return "葉"
        case .sand:   return "砂"
        case .water:  return "水"
        case .glass:  return "ガラス"
        }
    }

    var color: UIColor {
        switch self {
        case .grass:
            return UIColor(red: 0.34, green: 0.66, blue: 0.25, alpha: 1)
        case .dirt:
            return UIColor(red: 0.49, green: 0.34, blue: 0.21, alpha: 1)
        case .stone:
            return UIColor(red: 0.55, green: 0.55, blue: 0.56, alpha: 1)
        case .wood:
            return UIColor(red: 0.35, green: 0.22, blue: 0.12, alpha: 1)
        case .leaves:
            return UIColor(red: 0.20, green: 0.45, blue: 0.22, alpha: 1)
        case .sand:
            return UIColor(red: 0.88, green: 0.82, blue: 0.61, alpha: 1)
        case .water:
            return UIColor(red: 0.22, green: 0.55, blue: 0.95, alpha: 1)
        case .glass:
            return UIColor(red: 0.85, green: 0.92, blue: 1.0, alpha: 1)
        }
    }
}

final class MinecraftGameController: NSObject, ObservableObject, SCNViewDelegate, UIGestureRecognizerDelegate {
    @Published var selectedBlockType: BlockType = .grass
    @Published var flyMode: Bool = true

    let scene = SCNScene()
    let cameraNode = SCNNode()

    var position = SCNVector3(0.5, 24, 0.5)
    var yaw: Float = -0.5
    var pitch: Float = -0.75

    var moveInput: CGSize = .zero
    var verticalInput: CGFloat = 0

    private var blocks = [String: BlockType]()
    private var blockNodes = [String: SCNNode]()

    private var lastTime: TimeInterval = 0
    private var panStartYaw: Float = 0
    private var panStartPitch: Float = 0

    weak var scnView: SCNView?

    private lazy var geometries: [BlockType: SCNBox] = {
        var dict = [BlockType: SCNBox]()

        for type in BlockType.allCases {
            let box = SCNBox(width: 1, height: 1, length: 1, chamferRadius: 0)

            let material = SCNMaterial()
            material.diffuse.contents = type.color
            material.lightingModel = .lambert
            material.emission.contents = UIColor(white: 0.28, alpha: 1)

            if type == .water {
                material.transparency = 0.55
                material.doubleSided = true
            }

            if type == .glass {
                material.transparency = 0.28
                material.doubleSided = true
            }

            box.firstMaterial = material
            dict[type] = box
        }

        return dict
    }()

    private let hitOptions: [String: Any] = [
        SCNSceneHitTestOption.searchMode.rawValue: SCNHitTestSearchMode.closest.rawValue,
        SCNSceneHitTestOption.categoryBitMask.rawValue: Int(1)
    ]

    var panGesture: UIPanGestureRecognizer!
    var tapGesture: UITapGestureRecognizer!
    var longPressGesture: UILongPressGestureRecognizer!

    override init() {
        super.init()

        scene.background.contents = UIColor(red: 0.58, green: 0.82, blue: 1.0, alpha: 1)

        let camera = SCNCamera()
        camera.zNear = 0.1
        camera.zFar = 400
        camera.wantsHDR = true
        cameraNode.camera = camera
        scene.rootNode.addChildNode(cameraNode)

        createGestures()
        generateWorld(size: 22, depth: 11)
    }

    private func createGestures() {
        panGesture = UIPanGestureRecognizer(target: self, action: #selector(handlePan(_:)))
        panGesture.delegate = self
        panGesture.maximumNumberOfTouches = 1

        tapGesture = UITapGestureRecognizer(target: self, action: #selector(handleTap(_:)))
        tapGesture.delegate = self
        tapGesture.require(toFail: panGesture)

        longPressGesture = UILongPressGestureRecognizer(target: self, action: #selector(handleLongPress(_:)))
        longPressGesture.minimumPressDuration = 0.35
        longPressGesture.allowableMovement = 18
        longPressGesture.delegate = self

        panGesture.require(toFail: longPressGesture)
    }

    func attach(to view: SCNView) {
        scnView = view

        view.addGestureRecognizer(panGesture)
        view.addGestureRecognizer(tapGesture)
        view.addGestureRecognizer(longPressGesture)
    }

    private func blockKey(_ x: Int, _ y: Int, _ z: Int) -> String {
        return "\(x),\(y),\(z)"
    }

    private func parseKey(_ key: String) -> (x: Int, y: Int, z: Int)? {
        let parts = key.split(separator: ",")
        guard parts.count == 3,
              let x = Int(parts[0]),
              let y = Int(parts[1]),
              let z = Int(parts[2])
        else {
            return nil
        }
        return (x, y, z)
    }

    func setBlock(_ x: Int, _ y: Int, _ z: Int, _ type: BlockType) {
        let key = blockKey(x, y, z)

        if blocks[key] == type {
            return
        }

        if let old = blockNodes[key] {
            old.removeFromParentNode()
        }

        guard let geometry = geometries[type] else { return }

        let node = SCNNode(geometry: geometry)
        node.position = SCNVector3(CGFloat(x) + 0.5, CGFloat(y) + 0.5, CGFloat(z) + 0.5)
        node.name = key
        node.categoryBitMask = 1

        scene.rootNode.addChildNode(node)
        blocks[key] = type
        blockNodes[key] = node
    }

    func removeBlock(key: String) {
        if let node = blockNodes[key] {
            node.removeFromParentNode()
            blockNodes[key] = nil
            blocks[key] = nil
        }
    }

    private func generateWorld(size: Int, depth: Int) {
        let half = size / 2

        for x in -half...half {
            for z in -half...half {
                let h = Int(5.0 + 2.5 * sin(Float(x) * 0.23) * cos(Float(z) * 0.23))
                let topY = min(max(h, 1), depth - 2)

                for y in 0...topY {
                    let type: BlockType

                    if y == topY {
                        type = (topY <= 3) ? .sand : .grass
                    } else if topY - y <= 2 {
                        type = .dirt
                    } else {
                        type = .stone
                    }

                    setBlock(x, y, z, type)
                }

                if topY >= 4,
                   x % 11 == 0,
                   z % 13 == 0,
                   abs(x) < half - 2,
                   abs(z) < half - 2 {
                    addTree(x: x, z: z, groundY: topY)
                }
            }
        }
    }

    private func addTree(x: Int, z: Int, groundY: Int) {
        for y in (groundY + 1)...(groundY + 3) {
            setBlock(x, y, z, .wood)
        }

        let leafCenter = groundY + 4

        for dx in -2...2 {
            for dz in -2...2 {
                for dy in (leafCenter - 1)...(leafCenter + 1) {
                    let distance = abs(dx) + abs(dz) + abs(dy - leafCenter)

                    if distance <= 2 && !(dx == 0 && dz == 0 && dy < leafCenter) {
                        setBlock(x + dx, dy, z + dz, .leaves)
                    }
                }
            }
        }
    }

    func renderer(_ renderer: SCNSceneRenderer, updateAtTime time: TimeInterval) {
        let dt = max(0.0, min(time - lastTime, 0.1))
        lastTime = time

        let speed: CGFloat = flyMode ? 15.0 : 7.0

        let yawCG = CGFloat(yaw)
        let pitchCG = CGFloat(pitch)
        let cp = cos(pitchCG)

        let forward = SCNVector3(
            -sin(yawCG) * cp,
            sin(pitchCG),
            -cos(yawCG) * cp
        )

        let right = SCNVector3(
            cos(yawCG),
            0,
            sin(yawCG)
        )

        var mx = moveInput.width
        var my = moveInput.height

        let mag = hypot(mx, my)
        if mag > 1 {
            mx /= mag
            my /= mag
        }

        var vel = SCNVector3(0, 0, 0)

        vel.x = forward.x * my + right.x * mx
        vel.y = forward.y * my + verticalInput
        vel.z = forward.z * my + right.z * mx

        vel.x *= speed
        vel.y *= speed
        vel.z *= speed

        position.x += vel.x * CGFloat(dt)
        position.y += vel.y * CGFloat(dt)
        position.z += vel.z * CGFloat(dt)

        cameraNode.position = position
        cameraNode.eulerAngles = SCNVector3(CGFloat(pitch), CGFloat(yaw), 0)
    }

    @objc private func handlePan(_ gesture: UIPanGestureRecognizer) {
        switch gesture.state {
        case .began:
            panStartYaw = yaw
            panStartPitch = pitch

        case .changed:
            let t = gesture.translation(in: gesture.view)

            yaw = panStartYaw - Float(t.x) * 0.0035
            pitch = max(-1.45, min(1.45, panStartPitch - Float(t.y) * 0.0035))

        default:
            break
        }
    }

    @objc private func handleTap(_ gesture: UITapGestureRecognizer) {
        guard let view = scnView else { return }

        let hits = view.sceneHitTest(gesture.location(in: view), options: hitOptions)
        guard let hit = hits.first, let key = hit.node.name else { return }

        removeBlock(key: key)
    }

    @objc private func handleLongPress(_ gesture: UILongPressGestureRecognizer) {
        guard gesture.state == .began, let view = scnView else { return }

        let hits = view.sceneHitTest(gesture.location(in: view), options: hitOptions)
        guard let hit = hits.first,
              let key = hit.node.name,
              let c = parseKey(key)
        else {
            return
        }

        let nx = Int(hit.globalNormal.x.rounded())
        let ny = Int(hit.globalNormal.y.rounded())
        let nz = Int(hit.globalNormal.z.rounded())

        setBlock(c.x + nx, c.y + ny, c.z + nz, selectedBlockType)
    }

    func gestureRecognizer(
        _ gestureRecognizer: UIGestureRecognizer,
        shouldRecognizeSimultaneouslyWith otherGestureRecognizer: UIGestureRecognizer
    ) -> Bool {
        return gestureRecognizer === panGesture && otherGestureRecognizer === longPressGesture
    }
}

struct SceneContainer: UIViewRepresentable {
    let controller: MinecraftGameController

    func makeUIView(context: Context) -> SCNView {
        let view = SCNView(frame: .zero)

        view.scene = controller.scene
        view.pointOfView = controller.cameraNode

        view.delegate = controller
        view.isPlaying = true
        view.preferredFramesPerSecond = 60

        view.allowsCameraControl = false
        view.autoenablesDefaultLighting = true
        view.antialiasingMode = .multisampling4X

        view.backgroundColor = UIColor(red: 0.58, green: 0.82, blue: 1.0, alpha: 1)

        controller.attach(to: view)

        return view
    }

    func updateUIView(_ uiView: SCNView, context: Context) {}
}

struct Joystick: View {
    @Binding var value: CGSize
    @State private var knobOffset: CGSize = .zero

    private let radius: CGFloat = 58

    var body: some View {
        ZStack {
            Circle()
                .stroke(Color.white.opacity(0.35), lineWidth: 3)
                .frame(width: radius * 2, height: radius * 2)

            Circle()
                .fill(Color.white.opacity(0.55))
                .frame(width: 42, height: 42)
                .offset(knobOffset)
        }
        .contentShape(Circle())
        .gesture(
            DragGesture(minimumDistance: 0)
                .onChanged { gesture in
                    let x = gesture.translation.x
                    let y = gesture.translation.y

                    let distance = hypot(x, y)
                    let scale = min(1, distance / radius)

                    if distance < 0.001 {
                        knobOffset = .zero
                        value = .zero
                        return
                    }

                    let angle = atan2(y, x)
                    knobOffset = CGSize(
                        width: cos(angle) * scale * radius,
                        height: sin(angle) * scale * radius
                    )

                    value = CGSize(
                        width: knobOffset.width / radius,
                        height: -knobOffset.height / radius
                    )
                }
                .onEnded { _ in
                    knobOffset = .zero
                    value = .zero
                }
        )
    }
}

struct HotbarView: View {
    @ObservedObject var game: MinecraftGameController

    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                ForEach(BlockType.allCases) { type in
                    Button {
                        game.selectedBlockType = type
                    } label: {
                        VStack(spacing: 4) {
                            RoundedRectangle(cornerRadius: 6)
                                .fill(Color(type.color))
                                .frame(width: 44, height: 44)
                                .overlay(
                                    RoundedRectangle(cornerRadius: 6)
                                        .stroke(Color.white.opacity(0.55), lineWidth: 2)
                                )

                            Text(type.displayName)
                                .font(.caption2)
                                .foregroundColor(.white)
                        }
                        .padding(6)
                        .background(
                            RoundedRectangle(cornerRadius: 10)
                                .fill(Color.black.opacity(game.selectedBlockType == type ? 0.35 : 0.18))
                        )
                    }
                    .buttonStyle(.plain)
                }
            }
            .padding(.horizontal, 10)
        }
    }
}

struct ContentView: View {
    @StateObject private var game = MinecraftGameController()

    private var moveBinding: Binding<CGSize> {
        Binding(
            get: { game.moveInput },
            set: { game.moveInput = $0 }
        )
    }

    var body: some View {
        ZStack {
            SceneContainer(controller: game)
                .ignoresSafeArea()

            // クロスヘア
            Text("＋")
                .font(.system(size: 40, weight: .thin, design: .monospaced))
                .foregroundColor(.white.opacity(0.9))
                .shadow(radius: 2)
                .allowsHitTesting(false)

            VStack {
                HStack {
                    VStack(alignment: .leading, spacing: 6) {
                        Text("マイクラ風 3D箱庭")
                            .font(.headline)
                            .foregroundColor(.white)

                        Text("タップ: 破壊 / 長押し: 設置 / ドラッグ: 視点")
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.85))

                        Text("選択: \(game.selectedBlockType.displayName)")
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.95))

                        Text("モード: \(game.flyMode ? "飛行" : "通常")")
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.95))
                    }
                    .padding(12)
                    .background(
                        RoundedRectangle(cornerRadius: 12)
                            .fill(Color.black.opacity(0.35))
                    )

                    Spacer()
                }
                .padding()

                Spacer()

                HStack(alignment: .bottom) {
                    Joystick(value: moveBinding)
                        .padding(.leading, 24)

                    Spacer()

                    VStack(spacing: 12) {
                        Button {
                            game.flyMode.toggle()
                        } label: {
                            Text(game.flyMode ? "飛行" : "着地")
                                .foregroundColor(.white)
                                .padding(.horizontal, 14)
                                .padding(.vertical, 10)
                        }
                        .background(
                            RoundedRectangle(cornerRadius: 12)
                                .fill(Color.black.opacity(0.35))
                        )

                        verticalButton(symbol: "arrow.up", input: 1)
                        verticalButton(symbol: "arrow.down", input: -1)
                    }
                    .padding(.trailing, 24)
                }
                .padding(.bottom, 110)
            }

            VStack {
                Spacer()

                HotbarView(game: game)
                    .padding(.bottom, 18)
                    .padding(.horizontal, 8)
            }
        }
    }

    @ViewBuilder
    private func verticalButton(symbol: String, input: CGFloat) -> some View {
        Button(action: {}) {
            Image(systemName: symbol)
                .font(.title2)
                .foregroundColor(.white)
                .frame(width: 58, height: 58)
        }
        .background(
            RoundedRectangle(cornerRadius: 14)
                .fill(Color.black.opacity(0.35))
        )
        .simultaneousGesture(
            DragGesture(minimumDistance: 0)
                .onChanged { _ in
                    game.verticalInput = input
                }
                .onEnded { _ in
                    game.verticalInput = 0
                }
        )
    }
}

#Preview {
    ContentView()
}
```

---

## 1ファイル完結版が必要な場合

上の `ContentView.swift` 部分に加えて、プロジェクト作成直後の `App.swift` を次に置き換えれば、そのまま動きます。

```swift
import SwiftUI

@main
struct Minecraft3DSandboxApp: App {
    var body: Scene {
        WindowGroup {
            ContentView()
        }
    }
}
```

---

## 実装した要素

- 3D ボクセル風ワールド
- 草・土・石・木・葉・砂・水・ガラス
- 簡易地形生成
- 木生成
- ブロック破壊
- ブロック設置
- 画面ドラッグで視点回転
- ジョイスティック移動
- 飛行/着地
- ホットバーで設置ブロック選択

---

## 補足

これはフルの Minecraft ではなく、**モバイル用に簡略化した 3D 箱庭**です。  
本家 Minecraft っぽい拡張をするなら次を追加していくと良いです。

- 重力/当たり判定
- インベントリ
- クラフト
- モブ
- チャンク管理
- 永続保存
- テクスチャ画像
- ワイヤーフレーム表示
- 座標表示
- 範囲選択
- 地面スナップ配置

必要なら次に「当たり判定付き重力版」「インベントリ付き版」「Mac/iPad で WASD 版」も出せます。
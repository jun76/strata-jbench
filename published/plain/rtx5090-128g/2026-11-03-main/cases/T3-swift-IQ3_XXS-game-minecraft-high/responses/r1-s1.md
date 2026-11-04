iOS の Swift + SceneKit で動く「マイクラ風の 3D 箱庭」を 1 ファイルで作ります。

- **タップ**：ブロックを置く/壊す
- **ドラッグ**：カメラを回す
- **ボタン**：前・後ろ・左・右・上・下移動
- **ブロック選択**：草・土・石・木・ガラス
- **置/壊切替**：`置く` / `壊す`

## 使い方

1. Xcode で `App`（Storyboard 付き）を作る
2. `ViewController.swift` を下のコードに置き換える
3. `Main.storyboard` で View Controller のクラスを `GameViewController` に設定する
4. iPhone シミュレータ/実機で実行

---

## `ViewController.swift`

```swift
import UIKit
import SceneKit

final class GameViewController: UIViewController {
    private let scnView = SCNView()
    private let cameraNode = SCNNode()

    // ブロック座標 → ノード を保持する辞書
    private var blockNodes: [String: SCNNode] = [:]

    // カメラ角度
    private var yaw: Float = 0.0
    private var pitch: Float = -0.28

    // 選択中ブロック
    private var selectedType = "grass"

    // true: 置く / false: 壊す
    private var placing = true

    private var modeButton: UIButton!
    private var selectionButtons: [UIButton: String] = [:]

    override func viewDidLoad() {
        super.viewDidLoad()
        setupScene()
        generateWorld()
        setupUI()
        setupGestures()
        updateCamera()
    }

    override func viewDidLayoutSubviews() {
        super.viewDidLayoutSubviews()
        scnView.frame = view.bounds
    }

    // MARK: - Scene

    private func setupScene() {
        scnView.frame = view.bounds
        scnView.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        scnView.backgroundColor = UIColor(red: 0.55, green: 0.78, blue: 1.0, alpha: 1)
        scnView.allowsCameraControl = false
        scnView.antialiasingMode = .multisampling4X
        view.addSubview(scnView)

        let scene = SCNScene()
        scnView.scene = scene
        scene.background.contents = UIColor(red: 0.55, green: 0.78, blue: 1.0, alpha: 1)

        let camera = SCNCamera()
        camera.nearClippingDistance = 0.05
        camera.farClippingDistance = 400
        cameraNode.camera = camera
        cameraNode.position = SCNVector3(8.0, 9.0, 20.0)
        scene.rootNode.addChildNode(cameraNode)

        let ambient = SCNLight()
        ambient.type = .ambient
        ambient.color = UIColor(white: 0.95, alpha: 1.0)
        cameraNode.light = ambient
    }

    private func updateCamera() {
        pitch = min(1.25, max(-1.25, pitch))
        cameraNode.eulerAngles = SCNVector3(pitch, yaw, 0.0)
    }

    // MARK: - World generation

    private func heightAt(x: Int, z: Int) -> Int {
        let n = sin(Float(x) * 0.33) * cos(Float(z) * 0.33)
        return max(0, Int(1.0 + n * 2.0))
    }

    private func generateWorld() {
        let size = 16

        for x in 0..<size {
            for z in 0..<size {
                let h = heightAt(x: x, z: z)
                for y in 0...h {
                    let type: String
                    if y == h {
                        type = "grass"
                    } else if y >= h - 1 {
                        type = "dirt"
                    } else {
                        type = "stone"
                    }
                    addBlock(x: x, y: y, z: z, type: type)
                }
            }
        }

        // 木を適当に生成
        for (x, z) in [(3, 3), (10, 5), (6, 11)] {
            let base = heightAt(x: x, z: z)
            let trunkTop = base + 2

            for y in (base + 1)...trunkTop {
                addBlock(x: x, y: y, z: z, type: "wood")
            }

            for dx in -1...1 {
                for dz in -1...1 {
                    for dy in 0...1 {
                        addBlock(x: x + dx, y: trunkTop + 1 + dy, z: z + dz, type: "grass")
                    }
                }
            }
        }
    }

    private func key(_ x: Int, _ y: Int, _ z: Int) -> String {
        return "b:\(x):\(y):\(z)"
    }

    private func addBlock(x: Int, y: Int, z: Int, type: String) {
        guard y >= 0 && y < 50, x > -30, x < 50, z > -30, z < 50 else { return }

        let k = key(x, y, z)
        guard blockNodes[k] == nil else { return }

        let box = SCNBox(width: 1, height: 1, length: 1, chamferRadius: 0)
        box.materials = materials(for: type)

        let node = SCNNode(geometry: box)
        node.position = SCNVector3(Float(x) + 0.5, Float(y) + 0.5, Float(z) + 0.5)
        node.name = k

        scnView.scene?.rootNode.addChildNode(node)
        blockNodes[k] = node
    }

    private func removeBlock(key: String) {
        guard let node = blockNodes[key] else { return }
        node.removeFromParentNode()
        blockNodes.removeValue(forKey: key)
    }

    private func materials(for type: String) -> [SCNMaterial] {
        let grassTop = UIColor(red: 0.28, green: 0.65, blue: 0.23, alpha: 1.0)
        let dirt = UIColor(red: 0.62, green: 0.43, blue: 0.27, alpha: 1.0)
        let stone = UIColor(red: 0.55, green: 0.55, blue: 0.55, alpha: 1.0)
        let wood = UIColor(red: 0.74, green: 0.59, blue: 0.35, alpha: 1.0)
        let glass = UIColor(red: 0.65, green: 0.92, blue: 0.96, alpha: 1.0)

        func makeMaterial(_ color: UIColor, transparency: CGFloat = 1.0) -> SCNMaterial {
            let m = SCNMaterial()
            m.diffuse.contents = color
            m.specular.contents = UIColor(white: 0.22, alpha: 1.0)
            m.shininess = 0.2
            m.isDoubleSided = true

            if transparency < 1.0 {
                m.transparency = transparency
                m.blendingMode = .alpha
            }

            return m
        }

        switch type {
        case "grass":
            // SCNBox のマテリアルは 6 枚。上だけ緑にする
            return [
                makeMaterial(dirt),
                makeMaterial(dirt),
                makeMaterial(dirt),
                makeMaterial(dirt),
                makeMaterial(grassTop),
                makeMaterial(dirt)
            ]
        case "dirt":
            return Array(repeating: makeMaterial(dirt), count: 6)
        case "stone":
            return Array(repeating: makeMaterial(stone), count: 6)
        case "wood":
            return Array(repeating: makeMaterial(wood), count: 6)
        case "glass":
            return Array(repeating: makeMaterial(glass, transparency: 0.35), count: 6)
        default:
            return Array(repeating: makeMaterial(grassTop), count: 6)
        }
    }

    // MARK: - UI

    private func setupUI() {
        // 上段：ブロック選択と置/壊切替
        let topStack = UIStackView()
        topStack.axis = .horizontal
        topStack.spacing = 6
        topStack.distribution = .fillEqually
        topStack.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(topStack)

        NSLayoutConstraint.activate([
            topStack.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 8),
            topStack.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 8),
            topStack.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -8),
            topStack.heightAnchor.constraint(equalToConstant: 44)
        ])

        let blocks = [
            ("grass", "草"),
            ("dirt", "土"),
            ("stone", "石"),
            ("wood", "木"),
            ("glass", "ガラス")
        ]

        for (type, title) in blocks {
            let b = UIButton(type: .system)
            b.setTitle(title, for: .normal)
            b.titleLabel?.font = .systemFont(ofSize: 13)
            b.backgroundColor = UIColor(white: 0.18, alpha: 0.55)
            b.setTitleColor(.white, for: .normal)
            b.layer.cornerRadius = 6
            b.addTarget(self, action: #selector(selectBlock(_:)), for: .touchUpInside)
            selectionButtons[b] = type
            topStack.addArrangedSubview(b)
        }

        modeButton = UIButton(type: .system)
        modeButton.setTitle("置く", for: .normal)
        modeButton.titleLabel?.font = .systemFont(ofSize: 13)
        modeButton.backgroundColor = UIColor(red: 0.12, green: 0.62, blue: 0.18, alpha: 0.65)
        modeButton.setTitleColor(.white, for: .normal)
        modeButton.layer.cornerRadius = 6
        modeButton.addTarget(self, action: #selector(toggleMode), for: .touchUpInside)
        topStack.addArrangedSubview(modeButton)

        updateSelectionColors()

        // 下段：移動ボタン
        let moveStack = UIStackView()
        moveStack.axis = .vertical
        moveStack.spacing = 6
        moveStack.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(moveStack)

        NSLayoutConstraint.activate([
            moveStack.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 8),
            moveStack.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor, constant: -8),
            moveStack.widthAnchor.constraint(equalToConstant: 132)
        ])

        addMoveRow(to: moveStack, titles: ["前", "後"], selectors: [#selector(moveForward(_:)), #selector(moveBack(_:))])
        addMoveRow(to: moveStack, titles: ["左", "右"], selectors: [#selector(moveLeft(_:)), #selector(moveRight(_:))])
        addMoveRow(to: moveStack, titles: ["上", "下"], selectors: [#selector(moveUp(_:)), #selector(moveDown(_:))])
    }

    private func addMoveRow(to stack: UIStackView, titles: [String], selectors: [Selector]) {
        let row = UIStackView()
        row.axis = .horizontal
        row.spacing = 6
        row.distribution = .fillEqually
        row.heightAnchor.constraint(equalToConstant: 40).isActive = true

        for (index, title) in titles.enumerated() {
            let b = UIButton(type: .system)
            b.setTitle(title, for: .normal)
            b.titleLabel?.font = .systemFont(ofSize: 14)
            b.backgroundColor = UIColor(white: 0.18, alpha: 0.50)
            b.setTitleColor(.white, for: .normal)
            b.layer.cornerRadius = 6
            b.addTarget(self, action: selectors[index], for: .touchUpInside)
            row.addArrangedSubview(b)
        }

        stack.addArrangedSubview(row)
    }

    private func setupGestures() {
        let pan = UIPanGestureRecognizer(target: self, action: #selector(panCamera(_:)))
        pan.maximumNumberOfTouches = 1
        scnView.addGestureRecognizer(pan)

        let tap = UITapGestureRecognizer(target: self, action: #selector(tapScene(_:)))
        tap.require(toFail: pan)
        scnView.addGestureRecognizer(tap)
    }

    private func updateSelectionColors() {
        for (button, type) in selectionButtons {
            if type == selectedType {
                button.backgroundColor = UIColor(red: 0.15, green: 0.65, blue: 0.25, alpha: 0.85)
            } else {
                button.backgroundColor = UIColor(white: 0.18, alpha: 0.55)
            }
        }
    }

    // MARK: - Actions

    @objc private func selectBlock(_ sender: UIButton) {
        guard let type = selectionButtons[sender] else { return }
        selectedType = type
        updateSelectionColors()
    }

    @objc private func toggleMode() {
        placing.toggle()
        modeButton.setTitle(placing ? "置く" : "壊す", for: .normal)
        modeButton.backgroundColor = placing
            ? UIColor(red: 0.12, green: 0.62, blue: 0.18, alpha: 0.65)
            : UIColor(red: 0.85, green: 0.25, blue: 0.25, alpha: 0.65)
    }

    @objc private func panCamera(_ gesture: UIPanGestureRecognizer) {
        let translation = gesture.translation(in: scnView)
        yaw += Float(translation.x) * 0.01
        pitch -= Float(translation.y) * 0.01
        pitch = min(1.25, max(-1.25, pitch))
        cameraNode.eulerAngles = SCNVector3(pitch, yaw, 0.0)
        gesture.setTranslation(.zero, in: scnView)
    }

    @objc private func tapScene(_ gesture: UITapGestureRecognizer) {
        let point = gesture.location(in: scnView)

        let options: [SCNHitTestOption: Any] = [
            SCNHitTestOption.searchMode: SCNHitTestSearchMode.closest.rawValue,
            SCNHitTestOption.ignoreHiddenNodes: true,
            SCNHitTestOption.boundingBoxOnly: false
        ]

        let hits = scnView.hitTest(point, options: options)

        guard let hit = hits.first(where: { $0.node.name?.hasPrefix("b:") == true }) else { return }

        let node = hit.node
        guard let k = node.name else { return }

        if !placing {
            removeBlock(key: k)
            return
        }

        let x = Int(node.position.x.rounded(.down))
        let y = Int(node.position.y.rounded(.down))
        let z = Int(node.position.z.rounded(.down))

        let n = hit.localNormal
        let dx = abs(n.x) > 0.5 ? Int(n.x.rounded()) : 0
        let dy = abs(n.y) > 0.5 ? Int(n.y.rounded()) : 0
        let dz = abs(n.z) > 0.5 ? Int(n.z.rounded()) : 0

        addBlock(x: x + dx, y: y + dy, z: z + dz, type: selectedType)
    }

    // MARK: - Movement

    private func transformWorld(_ local: SCNVector3) -> SCNVector3 {
        SCNMatrix4Transform(cameraNode.worldTransform, local)
    }

    private func scale(_ v: SCNVector3, _ s: Float) -> SCNVector3 {
        SCNVector3(v.x * s, v.y * s, v.z * s)
    }

    private func moveBy(_ vector: SCNVector3) {
        let p = cameraNode.position
        cameraNode.position = SCNVector3(p.x + vector.x, p.y + vector.y, p.z + vector.z)
    }

    @objc private func moveForward(_ sender: UIButton) {
        moveBy(scale(transformWorld(SCNVector3(0, 0, -1)), 1.6))
    }

    @objc private func moveBack(_ sender: UIButton) {
        moveBy(scale(transformWorld(SCNVector3(0, 0, 1)), 1.6))
    }

    @objc private func moveLeft(_ sender: UIButton) {
        moveBy(scale(transformWorld(SCNVector3(-1, 0, 0)), 1.6))
    }

    @objc private func moveRight(_ sender: UIButton) {
        moveBy(scale(transformWorld(SCNVector3(1, 0, 0)), 1.6))
    }

    @objc private func moveUp(_ sender: UIButton) {
        moveBy(scale(transformWorld(SCNVector3(0, 1, 0)), 1.6))
    }

    @objc private func moveDown(_ sender: UIButton) {
        moveBy(scale(transformWorld(SCNVector3(0, -1, 0)), 1.6))
    }
}
```

---

## 操作方法

### カメラ操作
- **画面をドラッグ** → 視点回転

### ブロック操作
- **ブロック選択ボタン**で置く素材を選択
- `置く` モード：  
  タップした面の隣にブロックを追加
- `壊す` モード：  
  タップしたブロックを削除

### 移動
- `前`：進行方向へ移動
- `後`：後ろへ移動
- `左` / `右`：横移動
- `上` / `下`：上昇/下降

---

## 補足

これは「マイクラ風」の入門実装です。  
現行マイクラに近づけるなら、次を追加します。

- 重力・ジャンプ
- ブロック衝突判定
- 地形生成ノイズ
- 影
- セーブ/ロード
- 複数人マルチプレイ
- テクスチャ
- Sound
- UI 改善

まずはこのコードで、**iOS 上で動く 3D ボクセル箱庭**になります。
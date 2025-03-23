import React, { useEffect, useRef, useState } from "react";
import Matter from "matter-js";

const styles = {
    uploadContainer: {
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "100vh",
    },
    uploadButton: {
        padding: "12px 24px",
        background: "radial-gradient(#dcdcdc, #ffffff)", // グラデーション
        color: "black",
        fontSize: "18px",
        fontWeight: "bold",
        border: "none",
        borderRadius: "5px",
        cursor: "pointer",
        boxShadow: "0px 4px 6px rgba(0, 0, 0, 0.3)", // 立体感
    },
    uploadedImageContainer: {
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
    },
    button: {
        width: "150px",
        height: "60px",
        fontSize: "16px",
        fontWeight: "bold",
        backgroundColor: "black",
        color: "black",
        border: "none",
        borderRadius: "20px",
        cursor: "pointer",
        margin: "0px",
        background: "radial-gradient(#dcdcdc, #c0c0c0)", 
        boxShadow: "0px 4px 6px rgba(0, 0, 0, 0.3)", 
        transition: "all 0.2s ease-in-out",
        whiteSpace: "pre-line", // 改行を反映
    },
    buttonHover: {
        background: "radial-gradient(#ffffff, #dcdcdc)",
        boxShadow: "0px 2px 4px rgba(0, 0, 0, 0.2)",
        transform: "translateY(2px)", // クリック時の押し込み
    },
    buttonContainer: {
        position: "absolute",
        top: "515px",
        left: "950px",
        transform: "translate(-50%, -50%)",
        display: "flex",
        flexDirection: "column",
        gap: "6px",
    },
    scene: {
        width: "1060px",
        height: "700px",
        background: "linear-gradient(to bottom, #000000, #d3d3d3, #000000)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
    },
    description: {
        width: "1000px",
        fontSize: "18px",
        fontWeight: "bold",
        color: "#00ff33",
        background: "transparent",
        padding: "10px",
        borderRadius: "5px",
        position: "absolute",
        top: "20px",
        left: "30px",
        zIndex: 10,
    },
    loadingContainer: {
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        height: "100vh",
    },
    loadingText: {
        fontSize: "25px",
        color: "#00ff33",
        backgroundColor: "rgba(0, 0, 0, 0.5)", 
        marginBottom: "20px",
        padding: "10px",
        borderRadius: "5px"
    },        
    spinner: {
        border: "4px solid rgba(0,0,0,0.1)",
        width: "36px",
        height: "36px",
        backgroundColor: "rgba(0, 0, 0, 0.5)",
        borderRadius: "50%",
        borderLeftColor: "#09f",
        animation: "spin 1s linear infinite",
    },
};

const MatterSimulation = () => {
    const sceneRef = useRef(null);
    const [uploadedImage, setUploadedImage] = useState(null);
    const [similarImages, setSimilarImages] = useState([]);
    const [absorbedImages, setAbsorbedImages] = useState([]);
    const isReversedRef = useRef(false);
    const [isLoading, setIsLoading] = useState(false);// 読み込み中状態を管理
    const [isDescriptionVisible, setIsDescriptionVisible] = useState(false);
    const [hoveredIndex, setHoveredIndex] = useState(null);

    // 説明ボタンの切り替え処理
    const toggleDescription = () => {
        setIsDescriptionVisible(prev => !prev);
    };
    const [buttonLabel, setButtonLabel] = useState("似ている画像");
    const [isSaved, setIsSaved] = useState(false);
    // 引力/斥力 反転ボタンの切り替え処理
    const toggleReversed = () => {
        isReversedRef.current = !isReversedRef.current;
        setButtonLabel(isReversedRef.current ? "似ていない画像" : "似ている画像");
    };
    const handleReload = async () => {
    
        // 現在のサムネイル画像をクリア
        setSimilarImages([]);

        const formData = new FormData();
        
        try {
            // バックエンドのreloadエンドポイントにPOSTリクエストを送信
            const response = await fetch("your_backend/reload", {
                method: "POST",
                body: formData
            });
            const data = await response.json();
            // バックエンドから返された画像データでsimilarImagesを更新
            // ここではdata.similar_imagesが新しい画像リストであることを仮定
            setSimilarImages(data.similar_images);
        } catch (error) {
            console.error("Reload error:", error);
            alert(`リロード中にエラーが発生しました: ${error.message}`);
        }
    };

    const [modalImage, setModalImage] = useState(null);

    // 画像アップロード処理
    const handleUpload = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        setIsLoading(true);

        const formData = new FormData();
        formData.append("image", file);
        formData.append("num_img", 200);


        const response = await fetch("your_backend/upload", {
            method: "POST",
            body: formData,
        });

        const data = await response.json();
        // console.log(`Received ${data.similar_images.length} similar images`); // 返ってきたデータ数を表示
        // console.log(`Received ${data.num} num images`);
        // console.log(`Received ${data.num_total} num_total images`);

        setUploadedImage(URL.createObjectURL(file)); // フロントで画像表示
        setSimilarImages(data.similar_images);  // 類似画像リストをセット

        setIsLoading(false);
    };

    // 画像保存処理
    const handleSave = async () => {
        
        const response = await fetch("your_backend/save_image", {
            method: "POST",
            headers: { "Content-Type": "application/json" }
        });
    
        const data = await response.json();
        if (data.error) {
            alert(`保存エラー: ${data.error}`);
        } else {
            alert(`画像保存成功！\nサムネイルURL: ${data.thumbnail_url}`);
            setIsSaved(true);
        }
    };

    const buttons = [
        { label: isDescriptionVisible ? "説明を消す" : "説明", onClick: toggleDescription },
        { label: "Reload", onClick: handleReload },
        { label: buttonLabel, onClick: toggleReversed },
        { label: isSaved ? "保存済み" : "アップ画像を保存", onClick: handleSave, disabled: isSaved }
    ];

    useEffect(() => {
        if (!uploadedImage) return;

        const engine = Matter.Engine.create();
        const { world } = engine;

        const render = Matter.Render.create({
            element: sceneRef.current,
            engine: engine,
            options: {
                width: 1060,
                height: 700,
                wireframes: false,
                background: "transparent",
            },
        });

        const runner = Matter.Runner.create();
        Matter.Runner.run(runner, engine);

        function createGradientTexture() {
            const canvas = document.createElement("canvas");
            canvas.width = 180;
            canvas.height = 40;
            const ctx = canvas.getContext("2d");
        
            // グラデーションを作成
            const gradient = ctx.createLinearGradient(0, 0, 180, 0);
            gradient.addColorStop(0, "#8b0000"); // 赤
            gradient.addColorStop(0.5, "#dc143c"); 
            gradient.addColorStop(1, "#8b0000");
        
            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, canvas.width, canvas.height);
        
            return canvas.toDataURL(); // 画像としてエンコード
        }

        // 壁とゴール
        const ceiling = Matter.Bodies.rectangle(530, 0, 1060, 40, { isStatic: true, render: { fillStyle: "#000000" } });
        const ground = Matter.Bodies.rectangle(530, 680, 1060, 40, { isStatic: true, render: { fillStyle: "#000000" } });
        const goalArea = Matter.Bodies.rectangle(950, 350, 180, 40, { 
            isStatic: true, 
            render: { 
                sprite: {
                    texture: createGradientTexture(), // 生成したグラデーション画像を適用
                    xScale: 1.0,
                    yScale: 1.0
                }
             }
        });
        const leftWall = Matter.Bodies.rectangle(0, 350, 40, 700, { isStatic: true, render: { fillStyle: "#000000" } });
        const rightWall = Matter.Bodies.rectangle(850, 450, 20, 500, { isStatic: true, render: { fillStyle: "#000000" } });
        const rightwall2 = Matter.Bodies.rectangle(1060, 350, 40, 700, { isStatic: true, render: { fillStyle: "#000000" } });

        Matter.World.add(world, [ceiling, ground, leftWall, rightWall, goalArea, rightwall2]);

        const loadImageSize = (src) => {
            return new Promise((resolve) => {
                const img = new Image();
                img.src = src;
                img.onload = () => resolve({ width: img.width, height: img.height });
            });
        };

        (async () => {
            const playerSize = await loadImageSize(uploadedImage);

            const player = Matter.Bodies.circle(955, 280, 50, {
                restitution: 0.1,
                frictionAir: 0.2,
                density:1,
                render: {
                    sprite: {
                        texture: uploadedImage,
                        xScale: 100 / playerSize.width,
                        yScale: 100 / playerSize.height,
                    },
                },
            });
            Matter.World.add(world, player);
   
            // 画像を Matter.js の物理エンジンに追加
            let objects = similarImages.map((image, index) => {
                return Matter.Bodies.circle(50 + (index % 20) * 40, 100 + Math.floor(index / 20) * 50, 20, {
                    restitution: 0.1,
                    frictionAir: 0.2,
                    density:0.01,
                    render: { 
                        sprite: { 
                            texture: image.s3_thumbnail_url, 
                            xScale: 1.0, 
                            yScale: 1.0, 
                        } 
                    },
                    label: image,
                    similarity: image.similarity,
                });
            });

            Matter.World.add(world, objects);

            // マウスでオブジェクトを掴めるようにする
            const mouse = Matter.Mouse.create(render.canvas);
            const mouseConstraint = Matter.MouseConstraint.create(engine, {
                mouse,
                constraint: {
                    stiffness: 0.2,
                    render: { visible: false },
                },
            });

            Matter.World.add(world, mouseConstraint);
            render.mouse = mouse;

            Matter.Events.on(engine, "beforeUpdate", () => {
                objects.forEach((obj, index) => {
                    applyForce(obj, player, obj.similarity);
                });
            });
            
            
            
            function applyForce(obj, player, similarity) {
                //console.log(`Object ID: ${obj.id}, Similarity: ${similarity}`);

                const dx = player.position.x - obj.position.x;
                const dy = player.position.y - obj.position.y;
                const distanceSq = dx * dx + dy * dy + 1;

                // コサイン類似度をもとに引力・斥力を決定（反転を考慮）
                const forceDirection = isReversedRef.current ? -1 : 1; // 反転ボタンが押されたら方向を変える
                const forceMagnitude = (similarity * 15.0 * forceDirection) / distanceSq;
                obj.forceMagnitude = forceMagnitude;
                // if (Math.abs(forceMagnitude) > 0.0001) {
                //     console.log("similarity:", similarity, "forceMagnitude:", forceMagnitude);
                // }
                //console.log("similarity:", similarity, "forceMagnitude:", forceMagnitude);
                Matter.Body.applyForce(obj, obj.position, { x: dx * forceMagnitude, y: dy * forceMagnitude });
            }

            Matter.Events.on(engine, "collisionStart", (event) => {
                event.pairs.forEach(pair => {
                    if (pair.bodyA === goalArea || pair.bodyB === goalArea) {
                        const obj = pair.bodyA === goalArea ? pair.bodyB : pair.bodyA;
                        if (objects.includes(obj)) {
                            explodeAndRemove(obj);
                            objects = objects.filter(o => o !== obj);
                        }
                    }
                });
            });

            function explodeAndRemove(obj) {
                let fragments = [];
                
                for (let i = 0; i < 10; i++) {
                    const fragment = Matter.Bodies.circle(obj.position.x, obj.position.y, 5, {
                        restitution: 4,
                        frictionAir: 10,
                        render: { fillStyle: "red" },
                        collisionFilter: {
                          category: 0x0002,  // **独自のカテゴリを設定**
                          mask: 0x0000       // **他の物体と衝突しない**
                      }
                    });
                    
                    const angle = Math.random() * Math.PI * 2;
                    const force = 0.01 + Math.random() * 0.001; // **効果**
                    
                    Matter.Body.applyForce(fragment, fragment.position, {
                        x: Math.cos(angle) * force,
                        y: Math.sin(angle) * force,
                    });
            
                    fragments.push(fragment);
                }
                
                Matter.World.add(world, fragments);
            
                const fullSizeURL = obj.label?.s3_fullsize_url;
            
                // **オブジェクトを即時消去**
                Matter.World.remove(world, obj);
            
                setTimeout(() => {
                    fragments.forEach(f => Matter.World.remove(world, f));
                    if (fullSizeURL) {
                        setAbsorbedImages(prev => [...prev, { url: fullSizeURL, similarity: obj.similarity || 0 }]);
                    }
                }, 1000); // **エフェクトの時間を短縮**
            }
          
            Matter.Render.run(render);

        })();

        return () => {
            Matter.World.clear(world);
            Matter.Engine.clear(engine);
            Matter.Render.stop(render);
            Matter.Runner.stop(runner);
            render.canvas.remove();
        };
    }, [uploadedImage, similarImages]);

    return (
        <div>
            {/* 背景動画 */}
            {!uploadedImage && (
            <video
                autoPlay
                loop
                muted
                playsInline
                style={{
                position: "absolute",
                top: 0,
                left: 0,
                width: "100%",
                height: "100%",
                objectFit: "cover",
                zIndex: -1,
                }}
            >
                <source src="/background.mp4" type="video/mp4" />
                Your browser does not support the video tag.
            </video>
            )}

            {isLoading ? (
                <div style={styles.loadingContainer}>
                <p style={styles.loadingText}>準備中…</p>
                <div style={styles.spinner}></div>
                <style>{`
                    @keyframes spin {
                     to { transform: rotate(360deg); }
                    }
                `}</style>
              </div>
            ) : !uploadedImage ? (
                <div style={styles.uploadContainer}>
                    <label htmlFor="file-upload" style={styles.uploadButton}>
                        📂 画像ファイルを選択して下さい
                    </label>
                    <input 
                        id="file-upload" 
                        type="file" 
                        accept="image/*" 
                        onChange={handleUpload} 
                        style={{ display: "none" }} // input を非表示
                    />
                </div>
            ) : (
                <>
                    {/* シミュレーションエリアを左上に固定 */}
                    <div style={{ position: "absolute", top: 0, left: 0, zIndex: 0 }}>
                    <div ref={sceneRef} style={styles.scene} />
                    </div>

                    {/* アップロード画像をシミュレーションエリアの右隣に固定 */}
                    <div
                    style={{
                        position: "absolute",
                        top: 0,
                        left: "1060px", // シミュレーションエリアの幅 1060px
                        zIndex: 10,
                    }}
                    >
                    <img
                        src={uploadedImage}
                        alt="Uploaded"
                        style={{ height: "700px", width: "auto" }}
                    />
                    </div>

                    {/* ボタンコンテナ */}
                    <div style={styles.buttonContainer}>
                        {buttons.map((btn, index) => (
                            <button 
                                key={index}
                                style={{ 
                                    ...styles.button, 
                                    ...(hoveredIndex === index ? styles.buttonHover : {}), 
                                    ...btn.style 
                                }}
                                onMouseEnter={() => setHoveredIndex(index)}
                                onMouseLeave={() => setHoveredIndex(null)}
                                onClick={btn.onClick}
                                disabled={btn.disabled}
                            >
                                {btn.label.split("\n").map((line, i) => (
                                    <React.Fragment key={i}>
                                        {i > 0 && <br />}
                                        {line}
                                    </React.Fragment>
                                ))}
                            </button>
                        ))}
                    </div>

                    {/* 説明テキスト */}
                    {isDescriptionVisible && (
                        <div style={styles.description}>
                            <p>
                               赤い床の上にあるアップロードした画像をドラッグし、小さい画像を引きつけ赤い床に触れさせてください。<br />
                               <br />
                               消滅した画像は下部に類似度と共に表示され、クリックで拡大表示できます。画像はコレクションから選択されています。<br />
                               <br />
                               小さい画像は類似度がプラスで大きい値ほど近づこうとし、マイナスで小さいほど離れようとします。<br />
                               <br />
                               Reload 画像を更新、似ている画像 で引力と斥力を反転、アップ画像を保存 でアップ画像をコレクションに追加できます。
                            </p>
                        </div>
                    )}

                    {/* シミュレーションエリアの高さ分だけのプレースホルダー */}
                    <div style={{ marginTop: "720px" }}></div>
                    <div style={{ display: "flex", flexWrap: "wrap", gap: "10px", marginTop: "10px" }}>
                        {absorbedImages.map((item, index) => (
                          <div
                            key={index}
                            style={{
                                position: "relative",
                                width: "180px",
                                height: "180px",
                                cursor: "pointer",
                            }}
                            onClick={() => setModalImage(item.url)}
                          >
                            <img
                                src={item.url}
                                alt=""
                                width={180}
                                height={180}
                                style={{ display: "block" }}
                            />
                            <div
                                style={{
                                position: "absolute",
                                top: "50%",
                                left: "50%",
                                transform: "translate(-50%, -50%)",
                                color: "white",
                                fontSize: "24px",
                                fontWeight: "bold",
                                textShadow: "0 0 5px black",
                            }}
                          >
                            {item.similarity.toFixed(3)}
                            </div>
                        </div>
                        ))}
                    </div>
                    {modalImage && (
                        <div onClick={() => setModalImage(null)}
                            style={{ position: "fixed", top: 0, left: 0, zIndex: 20, width: "100vw", height: "100vh", background: "rgba(0,0,0,0.8)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                            <img src={modalImage} alt="Enlarged" style={{ maxWidth: "80%", maxHeight: "80%" }} />
                        </div>
                    )}
                </>
            )}
        </div>
    );
};

export default MatterSimulation;

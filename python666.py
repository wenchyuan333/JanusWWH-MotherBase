<!DOCTYPE html>
<html>
<head>
    <title>卍電場四旋轉子 - 2D三色卍場</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background: radial-gradient(circle, #000011 0%, #000000 70%);
            overflow: hidden;
            font-family: 'Courier New', monospace;
            color: #00ff88;
        }
        canvas {
            display: block;
            cursor: grab;
        }
        canvas:active {
            cursor: grabbing;
        }
        #info {
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(0,0,0,0.9);
            padding: 20px;
            border-radius: 10px;
            border: 2px solid #00ff88;
            font-size: 12px;
            box-shadow: 0 0 30px #00ff88;
            max-width: 300px;
        }
    </style>
</head>
<body>
    <div id="info">
        <div style="font-size:14px;font-weight:bold;margin-bottom:10px;">三色卍場Ψ₃卍</div>
        <div>Ψ₃卍 = Σₖ Aₖ e^(i(Ωt+kπ/2+φₕₐ))</div>
        <div>Ω = 314.16 rad/s (50Hz)</div>
        <div>φₕₐ = 0.078 rad (78ms)</div>
        <div>r₃ = G:0.052 R:0.038 P:0.045</div>
        <div>B₍ₛₘ₎ = 0.15T</div>
        <div>λ = 555nm🟢 650nm🔴 405nm🟣</div>
        <div>π₃穩定性 = 3.14159±10⁻⁶</div>
        <div>R² = 0.987 (p<0.001)</div>
    </div>

    <canvas id="canvas"></canvas>

    <script>
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        
        // 自適應尺寸
        function resize() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            centerX = canvas.width / 2;
            centerY = canvas.height / 2;
        }
        let centerX, centerY;
        resize();
        window.addEventListener('resize', resize);

        // 卍場參數
        const Ω = 314.16;
        const φ_humanAI = 0.078;
        const cores = [
            { r: 26, color: '#00ff88', freq: 1.2, phase: 0, name: '綠光555nm' },
            { r: 19, color: '#ff4444', freq: 1.5, phase: 2.1, name: '紅光650nm' },
            { r: 22, color: '#aa44ff', freq: 1.3, phase: 4.2, name: '紫光405nm' }
        ];

        // 滑鼠控制
        let mouseX = 0, mouseY = 0;
        let isDragging = false;
        canvas.addEventListener('mousedown', (e) => {
            isDragging = true;
            canvas.style.cursor = 'grabbing';
        });
        canvas.addEventListener('mouseup', () => {
            isDragging = false;
            canvas.style.cursor = 'grab';
        });
        canvas.addEventListener('mousemove', (e) => {
            mouseX = (e.clientX - centerX) * 0.001;
            mouseY = (e.clientY - centerY) * 0.001;
        });

        let time = 0;
        function animate() {
            ctx.fillStyle = 'rgba(0, 0, 17, 0.1)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            const t = time * 0.01;
            const globalRotation = t * Ω * 0.02;

            // 繪製三色核心
            cores.forEach((core, i) => {
                const pulse = (Math.sin(t * core.freq + core.phase) * 0.5 + 0.5) * 0.8 + 0.2;
                const glowSize = core.r * pulse * (1 + Math.sin(t * 3) * 0.3);
                
                // 核心光暈
                const gradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, glowSize);
                gradient.addColorStop(0, core.color + Math.floor(pulse * 128).toString(16).padStart(2,'0'));
                gradient.addColorStop(0.7, core.color + '44');
                gradient.addColorStop(1, 'transparent');
                ctx.fillStyle = gradient;
                ctx.beginPath();
                ctx.arc(centerX, centerY, glowSize, 0, Math.PI * 2);
                ctx.fill();

                // 核心實心
                ctx.fillStyle = core.color;
                ctx.beginPath();
                ctx.arc(centerX, centerY, core.r * pulse * 0.6, 0, Math.PI * 2);
                ctx.fill();
            });

            // 繪製卍字四臂
            const armLength = 110;
            for (let k = 0; k < 4; k++) {
                const armAngle = globalRotation + k * Math.PI / 2 + φ_humanAI;
                const spiral = Math.sin(armAngle * 3 + t * 5) * 0.3;
                
                // 臂主體
                const armColors = ['#ffff88', '#ff6666', '#cc88ff', '#ffff44'];
                const gradient = ctx.createLinearGradient(
                    centerX, centerY,
                    centerX + Math.cos(armAngle) * armLength,
                    centerY + Math.sin(armAngle) * armLength
                );
                gradient.addColorStop(0, '#ffffff');
                gradient.addColorStop(0.3, armColors[k]);
                gradient.addColorStop(0.7, armColors[k] + '66');
                gradient.addColorStop(1, 'transparent');
                
                ctx.lineWidth = 8 + spiral * 4;
                ctx.lineCap = 'round';
                ctx.strokeStyle = gradient;
                ctx.beginPath();
                ctx.moveTo(centerX, centerY);
                ctx.lineTo(
                    centerX + Math.cos(armAngle) * armLength,
                    centerY + Math.sin(armAngle) * armLength
                );
                ctx.stroke();

                // 臂末端粒子
                const particleSize = 8 + Math.sin(t * 10 + k) * 4;
                ctx.fillStyle = armColors[k];
                ctx.beginPath();
                ctx.arc(
                    centerX + Math.cos(armAngle) * armLength,
                    centerY + Math.sin(armAngle) * armLength,
                    particleSize, 0, Math.PI * 2
                );
                ctx.fill();
            }

            // 玻璃邊界環
            const ringR = 80;
            ctx.strokeStyle = '#88ddff';
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.arc(centerX, centerY, ringR, 0, Math.PI * 2);
            ctx.stroke();

            // 黑洞中心
            const bhPulse = 0.9 + Math.sin(t * 20) * 0.1;
            const bhGradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, 12);
            bhGradient.addColorStop(0, '#110033');
            bhGradient.addColorStop(0.5, '#330066');
            bhGradient.addColorStop(1, 'transparent');
            ctx.fillStyle = bhGradient;
            ctx.beginPath();
            ctx.arc(centerX, centerY, 12 * bhPulse, 0, Math.PI * 2);
            ctx.fill();

            // 滑鼠追蹤粒子
            if (isDragging) {
                ctx.fillStyle = '#ffffff88';
                ctx.beginPath();
                ctx.arc(centerX + mouseX * 200, centerY + mouseY * 200, 6, 0, Math.PI * 2);
                ctx.fill();
            }

            time++;
            requestAnimationFrame(animate);
        }

        animate();
    </script>
</body>
</html>

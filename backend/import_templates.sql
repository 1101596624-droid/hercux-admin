-- [1/24] 圆周运动 (physics, 75分)
INSERT INTO simulator_templates
(subject, topic, code, quality_score, visual_elements, line_count, has_setup_update, variable_count, created_at, metadata)
VALUES
('physics',
 '圆周运动',
 $HTML$<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>圆周运动 - Circular Motion</title>
    <style>
        body {
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background: #0f172a;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        canvas {
            border: 1px solid #334155;
            box-shadow: 0 0 30px rgba(59, 130, 246, 0.3);
        }
    </style>
</head>
<body>
    <canvas id="canvas" width="1200" height="800"></canvas>
    <script>
        const canvas = document.getElementById('canvas');
        const width = canvas.width;
        const height = canvas.height;

        // 学科配色
        const COLORS = {
            primary: '#3B82F6',
            secondary: '#F59E0B',
            accent: '#8B5CF6',
            background: '#1E293B',
            text: '#F1F5F9',
            success: '#10B981',
            danger: '#EF4444',
            grid: '#334155'
        };

        // Easing functions
        const Easing = {
            linear: t => t,
            easeIn: t => t * t,
            easeOut: t => t * (2 - t),
            easeInOut: t => t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t,
            easeOutBack: t => {
                const c1 = 1.70158;
                const c3 = c1 + 1;
                return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2);
            },
            easeInCubic: t => t * t * t,
            easeOutCubic: t => 1 - Math.pow(1 - t, 3)
        };

        function setup(ctx) {
            return {
                angle: 0,
                angularVelocity: 0.02,
                radius: width * 0.15,
                centerX: width * 0.5,
                centerY: height * 0.5,
                isAccelerating: false,
                dragPoint: null,
                showVectors: true,
                particles: [],
                trail: [],
                maxTrailLength: 80,
                isDragging: false,
                dragTarget: null,
                // Smooth display values
                displayRadius: width * 0.15,
                displayAngularVelocity: 0.02,
                // Speed control
                speedOptions: [0.25, 0.5, 1, 2, 4],
                currentSpeedIndex: 2  // Default to 1x
            };
        }

        function update(ctx, state, time, vars) {
            const t = time / 1000;

            // Update speed from state
            vars.speed = state.speedOptions[state.currentSpeedIndex];

            // Smooth interpolation for display values
            const smoothFactor = 0.2;
            state.displayRadius = state.displayRadius * (1 - smoothFactor) + state.radius * smoothFactor;
            state.displayAngularVelocity = state.displayAngularVelocity * (1 - smoothFactor) + state.angularVelocity * smoothFactor;

            // Clear canvas with fade effect
            ctx.setFillStyle(COLORS.background);
            ctx.setOpacity(0.3);
            ctx.drawRect(0, 0, width, height);
            ctx.setOpacity(1.0);

            // Background grid
            drawGrid(ctx, 50);

            // Update physics
            if (state.isAccelerating) {
                state.angularVelocity += 0.0005 * vars.speed;
            } else {
                state.angularVelocity = Math.max(0.01, state.angularVelocity * 0.998);
            }
            state.angle += state.angularVelocity * vars.speed;

            // Calculate positions
            const particleX = state.centerX + state.radius * Math.cos(state.angle);
            const particleY = state.centerY + state.radius * Math.sin(state.angle);

            // Calculate velocities
            const velocityX = -state.radius * state.angularVelocity * Math.sin(state.angle);
            const velocityY = state.radius * state.angularVelocity * Math.cos(state.angle);
            const speed = Math.sqrt(velocityX * velocityX + velocityY * velocityY);

            // Calculate centripetal acceleration
            const centripetalAccel = state.radius * state.angularVelocity * state.angularVelocity;
            const accelX = -centripetalAccel * Math.cos(state.angle);
            const accelY = -centripetalAccel * Math.sin(state.angle);

            // Trail management
            state.trail.push({ x: particleX, y: particleY, time: t });
            if (state.trail.length > state.maxTrailLength) {
                state.trail.shift();
            }

            // Draw trail
            drawTrail(ctx, state.trail, t);

            // Draw circular path
            drawCircularPath(ctx, state.centerX, state.centerY, state.radius);

            // Draw center point
            drawCenterPoint(ctx, state.centerX, state.centerY);

            // Draw radius line
            drawRadiusLine(ctx, state.centerX, state.centerY, particleX, particleY);

            // Draw particle with glow
            drawParticle(ctx, particleX, particleY, t);

            // Draw vectors
            if (state.showVectors) {
                const vectorScale = width * 0.08;

                // Velocity vector (tangent)
                drawVector(ctx, particleX, particleY,
                    velocityX / speed * vectorScale,
                    velocityY / speed * vectorScale,
                    COLORS.success, 'v', t);

                // Centripetal acceleration vector
                drawVector(ctx, particleX, particleY,
                    accelX / centripetalAccel * vectorScale * 1.2,
                    accelY / centripetalAccel * vectorScale * 1.2,
                    COLORS.danger, 'a', t);
            }

            // Draw angular velocity arc
            drawAngularVelocityArc(ctx, state.centerX, state.centerY, state.angle, state.radius * 0.3);

            // Draw info panels
            drawInfoPanel(ctx, width * 0.02, height * 0.02, [
                `角速度 ω: ${state.displayAngularVelocity.toFixed(4)} rad/s`,
                `线速度 v: ${speed.toFixed(2)} px/s`,
                `向心加速度 a: ${centripetalAccel.toFixed(2)} px/s²`,
                `半径 r: ${state.displayRadius.toFixed(0)} px`,
                `周期 T: ${(2 * Math.PI / state.angularVelocity).toFixed(2)} s`
            ]);

            // Draw control panel with sliders
            drawControlPanel(ctx, state, width * 0.02, height * 0.45);

            // Draw speed control
            drawSpeedControl(ctx, state, width * 0.02, height * 0.75);

            // Draw decorative elements
            drawDecorativeRings(ctx, state.centerX, state.centerY, state.radius, t);

            // Update particle effects
            updateParticleEffects(ctx, state, particleX, particleY, t);

            // Draw title
            drawTitle(ctx, width * 0.5, height * 0.05, '圆周运动模拟');

            // Draw angle indicator
            drawAngleIndicator(ctx, state.centerX, state.centerY, state.angle, state.radius * 0.2);
        }

        // Helper functions (12+ required)

        function drawGrid(ctx, spacing) {
            ctx.setStrokeStyle(COLORS.grid);
            ctx.setOpacity(0.1);
            ctx.setLineWidth(1);

            for (let x = 0; x < width; x += spacing) {
                ctx.drawLine(x, 0, x, height);
            }
            for (let y = 0; y < height; y += spacing) {
                ctx.drawLine(0, y, width, y);
            }
            ctx.setOpacity(1.0);
        }

        function drawCircularPath(ctx, cx, cy, radius) {
            ctx.setStrokeStyle(COLORS.primary);
            ctx.setOpacity(0.3);
            ctx.setLineWidth(2);
            ctx.setLineDash([10, 5]);
            ctx.drawCircle(cx, cy, radius);
            ctx.setLineDash([]);
            ctx.setOpacity(1.0);
        }

        function drawCenterPoint(ctx, x, y) {
            ctx.setFillStyle(COLORS.accent);
            ctx.setGlow(COLORS.accent, 15);
            ctx.drawCircle(x, y, 8);
            ctx.setGlow(null, 0);

            ctx.setFillStyle(COLORS.text);
            ctx.setFontSize(14);
            ctx.drawText('O', x + 15, y - 10);
        }

        function drawRadiusLine(ctx, cx, cy, px, py) {
            ctx.setStrokeStyle(COLORS.secondary);
            ctx.setOpacity(0.5);
            ctx.setLineWidth(2);
            ctx.drawLine(cx, cy, px, py);
            ctx.setOpacity(1.0);

            // Draw "r" label
            const midX = (cx + px) / 2;
            const midY = (cy + py) / 2;
            ctx.setFillStyle(COLORS.secondary);
            ctx.setFontSize(16);
            ctx.drawText('r', midX + 10, midY - 10);
        }

        function drawParticle(ctx, x, y, t) {
            // Outer glow
            ctx.setFillStyle(COLORS.primary);
            ctx.setGlow(COLORS.primary, 30);
            ctx.drawCircle(x, y, 20);
            ctx.setGlow(null, 0);

            // Core
            ctx.setFillStyle('#FFFFFF');
            ctx.drawCircle(x, y, 12);

            // Pulsing inner core
            const pulseSize = 6 + Math.sin(t * 5) * 2;
            ctx.setFillStyle(COLORS.primary);
            ctx.drawCircle(x, y, pulseSize);
        }

        function drawVector(ctx, x, y, dx, dy, color, label, t) {
            const arrowSize = 12;
            const angle = Math.atan2(dy, dx);
            const length = Math.sqrt(dx * dx + dy * dy);

            // Vector line with glow
            ctx.setStrokeStyle(color);
            ctx.setLineWidth(3);
            ctx.setGlow(color, 10);
            ctx.drawLine(x, y, x + dx, y + dy);
            ctx.setGlow(null, 0);

            // Arrowhead
            ctx.setFillStyle(color);
            const tipX = x + dx;
            const tipY = y + dy;

            ctx.drawPath([
                { x: tipX, y: tipY },
                { x: tipX - arrowSize * Math.cos(angle - Math.PI / 6),
                  y: tipY - arrowSize * Math.sin(angle - Math.PI / 6) },
                { x: tipX - arrowSize * Math.cos(angle + Math.PI / 6),
                  y: tipY - arrowSize * Math.sin(angle + Math.PI / 6) }
            ], true);

            // Label
            ctx.setFillStyle(color);
            ctx.setFontSize(18);
            ctx.drawText(label, tipX + 15, tipY - 10);
        }

        function drawTrail(ctx, trail, currentTime) {
            if (trail.length < 2) return;

            for (let i = 0; i < trail.length - 1; i++) {
                const progress = i / trail.length;
                const opacity = Easing.easeOut(progress) * 0.6;
                const size = Easing.easeOut(progress) * 4 + 2;

                ctx.setFillStyle(COLORS.primary);
                ctx.setOpacity(opacity);
                ctx.drawCircle(trail[i].x, trail[i].y, size);
            }
            ctx.setOpacity(1.0);
        }

        function drawAngularVelocityArc(ctx, cx, cy, angle, radius) {
            ctx.setStrokeStyle(COLORS.accent);
            ctx.setLineWidth(2);
            ctx.setOpacity(0.6);

            // Draw arc from 0 to current angle
            const steps = 30;
            const endAngle = angle % (2 * Math.PI);
            for (let i = 0; i < steps; i++) {
                const a1 = (i / steps) * endAngle;
                const a2 = ((i + 1) / steps) * endAngle;
                const x1 = cx + radius * Math.cos(a1);
                const y1 = cy + radius * Math.sin(a1);
                const x2 = cx + radius * Math.cos(a2);
                const y2 = cy + radius * Math.sin(a2);
                ctx.drawLine(x1, y1, x2, y2);
            }

            ctx.setOpacity(1.0);

            // Draw omega symbol
            ctx.setFillStyle(COLORS.accent);
            ctx.setFontSize(20);
            ctx.drawText('ω', cx + radius * 1.3, cy);
        }

        function drawInfoPanel(ctx, x, y, lines) {
            const padding = 15;
            const lineHeight = 25;
            const panelWidth = width * 0.25;
            const panelHeight = lines.length * lineHeight + padding * 2;

            // Panel background
            ctx.setFillStyle(COLORS.background);
            ctx.setOpacity(0.85);
            ctx.drawRect(x, y, panelWidth, panelHeight);
            ctx.setOpacity(1.0);

            // Border with glow
            ctx.setStrokeStyle(COLORS.primary);
            ctx.setLineWidth(2);
            ctx.setGlow(COLORS.primary, 8);
            ctx.drawRect(x, y, panelWidth, panelHeight);
            ctx.setGlow(null, 0);

            // Text lines
            ctx.setFillStyle(COLORS.text);
            ctx.setFontSize(16);
            lines.forEach((line, i) => {
                ctx.drawText(line, x + padding, y + padding + (i + 1) * lineHeight);
            });
        }

        function drawControlPanel(ctx, state, x, y) {
            const padding = 15;
            const panelWidth = width * 0.25;
            const panelHeight = height * 0.25;

            // Panel background
            ctx.setFillStyle(COLORS.background);
            ctx.setOpacity(0.85);
            ctx.drawRect(x, y, panelWidth, panelHeight);
            ctx.setOpacity(1.0);

            // Border
            ctx.setStrokeStyle(COLORS.secondary);
            ctx.setLineWidth(2);
            ctx.drawLine(x, y, x + panelWidth, y);
            ctx.drawLine(x + panelWidth, y, x + panelWidth, y + panelHeight);
            ctx.drawLine(x + panelWidth, y + panelHeight, x, y + panelHeight);
            ctx.drawLine(x, y + panelHeight, x, y);

            // Title
            ctx.setFillStyle(COLORS.text);
            ctx.setFontSize(16);
            ctx.drawText('控制面板', x + padding, y + padding + 20);

            // Radius slider
            ctx.setFontSize(14);
            ctx.drawText(`半径: ${state.displayRadius.toFixed(0)} px`, x + padding, y + padding + 50);
            drawSlider(ctx, x + padding, y + padding + 60, panelWidth - padding * 2, state.displayRadius, width * 0.08, width * 0.25, COLORS.accent);

            // Angular velocity slider
            ctx.drawText(`角速度: ${state.displayAngularVelocity.toFixed(3)} rad/s`, x + padding, y + padding + 100);
            drawSlider(ctx, x + padding, y + padding + 110, panelWidth - padding * 2, state.displayAngularVelocity, 0.01, 0.08, COLORS.primary);

            // Instructions
            ctx.setFontSize(12);
            ctx.drawText('• 拖拽滑块调节参数', x + padding, y + padding + 150);
            ctx.drawText('• 点击圆心加速', x + padding, y + padding + 170);
        }

        function drawSlider(ctx, x, y, w, value, min, max, color) {
            // Track
            ctx.setStrokeStyle(COLORS.grid);
            ctx.setLineWidth(4);
            ctx.drawLine(x, y, x + w, y);

            // Progress
            const progress = (value - min) / (max - min);
            ctx.setStrokeStyle(color);
            ctx.setLineWidth(4);
            ctx.drawLine(x, y, x + w * progress, y);

            // Handle
            ctx.setFillStyle(color);
            ctx.setGlow(color, 15);
            ctx.drawCircle(x + w * progress, y, 8);
            ctx.setGlow(null, 0);
        }

        function drawSpeedControl(ctx, state, x, y) {
            const panelWidth = width * 0.25;
            const panelHeight = height * 0.12;
            const padding = 15;

            // Panel background
            ctx.setFillStyle(COLORS.background);
            ctx.setOpacity(0.9);
            ctx.drawRect(x, y, panelWidth, panelHeight);
            ctx.setOpacity(1.0);

            // Border
            ctx.setStrokeStyle(COLORS.success);
            ctx.setLineWidth(2);
            ctx.drawLine(x, y, x + panelWidth, y);
            ctx.drawLine(x + panelWidth, y, x + panelWidth, y + panelHeight);
            ctx.drawLine(x + panelWidth, y + panelHeight, x, y + panelHeight);
            ctx.drawLine(x, y + panelHeight, x, y);

            // Title
            ctx.setFillStyle(COLORS.text);
            ctx.setFontSize(14);
            ctx.drawText('播放速度:', x + padding, y + 25);

            // Speed buttons
            const buttonWidth = 45;
            const buttonHeight = 28;
            const buttonSpacing = 6;
            const startX = x + padding;
            const buttonY = y + 40;

            state.speedOptions.forEach((speed, index) => {
                const buttonX = startX + index * (buttonWidth + buttonSpacing);
                const isActive = state.currentSpeedIndex === index;

                // Button background
                ctx.setFillStyle(isActive ? COLORS.success : COLORS.grid);
                ctx.setOpacity(isActive ? 1.0 : 0.5);
                ctx.drawRect(buttonX, buttonY, buttonWidth, buttonHeight);
                ctx.setOpacity(1.0);

                // Button border
                ctx.setStrokeStyle(isActive ? COLORS.success : COLORS.grid);
                ctx.setLineWidth(2);
                if (isActive) ctx.setGlow(COLORS.success, 10);
                ctx.drawLine(buttonX, buttonY, buttonX + buttonWidth, buttonY);
                ctx.drawLine(buttonX + buttonWidth, buttonY, buttonX + buttonWidth, buttonY + buttonHeight);
                ctx.drawLine(buttonX + buttonWidth, buttonY + buttonHeight, buttonX, buttonY + buttonHeight);
                ctx.drawLine(buttonX, buttonY + buttonHeight, buttonX, buttonY);
                ctx.setGlow(null, 0);

                // Button text
                ctx.setFillStyle(COLORS.text);
                ctx.setFontSize(12);
                const label = speed === 1 ? '1x' : speed < 1 ? `${speed}x` : `${speed}x`;
                const textOffset = label.length === 2 ? 11 : label.length === 3 ? 7 : 14;
                ctx.drawText(label, buttonX + textOffset, buttonY + buttonHeight / 2 + 4);
            });
        }

        function drawDecorativeRings(ctx, cx, cy, radius, t) {
            for (let i = 0; i < 3; i++) {
                const ringRadius = radius * (1.2 + i * 0.15);
                const phase = t * 0.5 + i * Math.PI * 0.66;
                const opacity = (Math.sin(phase) * 0.5 + 0.5) * 0.15;

                ctx.setStrokeStyle(COLORS.accent);
                ctx.setOpacity(opacity);
                ctx.setLineWidth(1);
                ctx.drawCircle(cx, cy, ringRadius);
            }
            ctx.setOpacity(1.0);
        }

        function updateParticleEffects(ctx, state, x, y, t) {
            // Emit particles periodically
            if (Math.random() < 0.1) {
                state.particles.push({
                    x: x,
                    y: y,
                    vx: (Math.random() - 0.5) * 2,
                    vy: (Math.random() - 0.5) * 2,
                    life: 1.0,
                    size: Math.random() * 3 + 2,
                    color: Math.random() > 0.5 ? COLORS.primary : COLORS.secondary
                });
            }

            // Update and draw particles
            state.particles = state.particles.filter(p => {
                p.x += p.vx;
                p.y += p.vy;
                p.life -= 0.02;

                if (p.life > 0) {
                    ctx.setFillStyle(p.color);
                    ctx.setOpacity(p.life * 0.6);
                    ctx.drawCircle(p.x, p.y, p.size * p.life);
                    return true;
                }
                return false;
            });
            ctx.setOpacity(1.0);
        }

        function drawTitle(ctx, x, y, text) {
            ctx.setFillStyle(COLORS.text);
            ctx.setFontSize(32);
            ctx.setGlow(COLORS.primary, 15);
            ctx.drawText(text, x - text.length * 8, y);
            ctx.setGlow(null, 0);
        }

        function drawAngleIndicator(ctx, cx, cy, angle, radius) {
            const normalizedAngle = ((angle % (2 * Math.PI)) * 180 / Math.PI).toFixed(1);

            // Draw angle arc
            ctx.setStrokeStyle(COLORS.secondary);
            ctx.setLineWidth(2);
            ctx.setOpacity(0.5);

            const steps = 20;
            for (let i = 0; i < steps; i++) {
                const a1 = (i / steps) * (angle % (2 * Math.PI));
                const a2 = ((i + 1) / steps) * (angle % (2 * Math.PI));
                const x1 = cx + radius * Math.cos(a1);
                const y1 = cy + radius * Math.sin(a1);
                const x2 = cx + radius * Math.cos(a2);
                const y2 = cy + radius * Math.sin(a2);
                ctx.drawLine(x1, y1, x2, y2);
            }
            ctx.setOpacity(1.0);

            // Draw angle text
            ctx.setFillStyle(COLORS.secondary);
            ctx.setFontSize(14);
            ctx.drawText(`θ = ${normalizedAngle}°`, cx + radius * 1.5, cy + radius * 0.5);
        }

        // Mock context implementation
        function createMockContext(canvas) {
            const realCtx = canvas.getContext('2d');
            let currentGlow = { color: null, blur: 0 };

            const ctx = {
                setFillStyle(color) {
                    realCtx.fillStyle = color;
                },
                setStrokeStyle(color) {
                    realCtx.strokeStyle = color;
                },
                setLineWidth(width) {
                    realCtx.lineWidth = width;
                },
                setOpacity(alpha) {
                    realCtx.globalAlpha = alpha;
                },
                setFontSize(size) {
                    realCtx.font = `${size}px 'Segoe UI', sans-serif`;
                },
                setLineDash(segments) {
                    realCtx.setLineDash(segments);
                },
                setGlow(color, blur) {
                    if (color) {
                        realCtx.shadowColor = color;
                        realCtx.shadowBlur = blur;
                    } else {
                        realCtx.shadowColor = 'transparent';
                        realCtx.shadowBlur = 0;
                    }
                },
                drawRect(x, y, w, h) {
                    realCtx.fillRect(x, y, w, h);
                },
                drawCircle(x, y, radius) {
                    realCtx.beginPath();
                    realCtx.arc(x, y, radius, 0, Math.PI * 2);
                    realCtx.fill();
                },
                drawLine(x1, y1, x2, y2) {
                    realCtx.beginPath();
                    realCtx.moveTo(x1, y1);
                    realCtx.lineTo(x2, y2);
                    realCtx.stroke();
                },
                drawText(text, x, y) {
                    realCtx.fillText(text, x, y);
                },
                drawPath(points, close = false) {
                    if (points.length === 0) return;
                    realCtx.beginPath();
                    realCtx.moveTo(points[0].x, points[0].y);
                    for (let i = 1; i < points.length; i++) {
                        realCtx.lineTo(points[i].x, points[i].y);
                    }
                    if (close) realCtx.closePath();
                    realCtx.fill();
                },
                onClick(callback) {
                    canvas.addEventListener('click', (e) => {
                        const rect = canvas.getBoundingClientRect();
                        callback(e.clientX - rect.left, e.clientY - rect.top);
                    });
                },
                onDrag(callback) {
                    let dragging = false;
                    canvas.addEventListener('mousedown', (e) => {
                        dragging = true;
                        const rect = canvas.getBoundingClientRect();
                        callback(e.clientX - rect.left, e.clientY - rect.top, 'start');
                    });
                    canvas.addEventListener('mousemove', (e) => {
                        if (dragging) {
                            const rect = canvas.getBoundingClientRect();
                            callback(e.clientX - rect.left, e.clientY - rect.top, 'move');
                        }
                    });
                    canvas.addEventListener('mouseup', () => {
                        if (dragging) {
                            dragging = false;
                            callback(0, 0, 'end');
                        }
                    });
                }
            };

            return ctx;
        }

        // Initialize context
        const ctx = createMockContext(canvas);

        // Setup interactions
        ctx.onClick((x, y) => {
            const dx = x - state.centerX;
            const dy = y - state.centerY;
            const dist = Math.sqrt(dx * dx + dy * dy);

            if (dist < 30) {
                state.isAccelerating = !state.isAccelerating;
            }

            // Check speed control buttons
            const speedPanelX = width * 0.02;
            const speedPanelY = height * 0.75;
            const padding = 15;
            const buttonWidth = 45;
            const buttonHeight = 28;
            const buttonSpacing = 6;
            const startX = speedPanelX + padding;
            const speedButtonY = speedPanelY + 40;

            state.speedOptions.forEach((speed, index) => {
                const buttonX = startX + index * (buttonWidth + buttonSpacing);
                if (x >= buttonX && x <= buttonX + buttonWidth &&
                    y >= speedButtonY && y <= speedButtonY + buttonHeight) {
                    state.currentSpeedIndex = index;
                }
            });
        });

        // Setup drag interaction for sliders
        ctx.onDrag((x, y, phase) => {
            const controlX = width * 0.02;
            const controlY = height * 0.45;
            const panelWidth = width * 0.25;
            const padding = 15;
            const sliderWidth = panelWidth - padding * 2;

            if (phase === 'start') {
                const radiusSliderY = controlY + padding + 60;
                const velocitySliderY = controlY + padding + 110;

                // Check radius slider
                if (x >= controlX + padding && x <= controlX + panelWidth - padding &&
                    y >= radiusSliderY - 10 && y <= radiusSliderY + 10) {
                    state.isDragging = true;
                    state.dragTarget = 'radius';
                }
                // Check velocity slider
                else if (x >= controlX + padding && x <= controlX + panelWidth - padding &&
                    y >= velocitySliderY - 10 && y <= velocitySliderY + 10) {
                    state.isDragging = true;
                    state.dragTarget = 'velocity';
                }
            } else if (phase === 'move' && state.isDragging) {
                const progress = Math.max(0, Math.min(1, (x - (controlX + padding)) / sliderWidth));

                if (state.dragTarget === 'radius') {
                    const minRadius = width * 0.08;
                    const maxRadius = width * 0.25;
                    state.radius = minRadius + progress * (maxRadius - minRadius);
                } else if (state.dragTarget === 'velocity') {
                    state.angularVelocity = 0.01 + progress * 0.07;
                }
            } else if (phase === 'end') {
                state.isDragging = false;
                state.dragTarget = null;
            }
        });

        // Animation loop
        const state = setup(ctx);
        const vars = { speed: 1.0 };
        let startTime = Date.now();

        function animate() {
            const time = Date.now() - startTime;
            update(ctx, state, time, vars);
            requestAnimationFrame(animate);
        }

        animate();
    </script>
</body>
</html>$HTML$,
 75,
 155,
 732,
 false,
 0,
 NOW(),
 '{"name": "圆周运动", "description": "展示物体做圆周运动的轨迹、向心力和角速度的关系", "difficulty": "medium", "render_mode": "html"}');


-- [2/24] 抛体运动 (physics, 75分)
INSERT INTO simulator_templates
(subject, topic, code, quality_score, visual_elements, line_count, has_setup_update, variable_count, created_at, metadata)
VALUES
('physics',
 '抛体运动',
 $HTML$<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>抛体运动 - Projectile Motion</title>
    <style>
        body {
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background: #0f172a;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        canvas {
            border: 1px solid #334155;
            box-shadow: 0 0 30px rgba(245, 158, 11, 0.3);
        }
    </style>
</head>
<body>
    <canvas id="canvas" width="1200" height="800"></canvas>
    <script>
        const canvas = document.getElementById('canvas');
        const width = canvas.width;
        const height = canvas.height;

        // 学科配色
        const COLORS = {
            primary: '#3B82F6',
            secondary: '#F59E0B',
            accent: '#8B5CF6',
            background: '#1E293B',
            text: '#F1F5F9',
            success: '#10B981',
            danger: '#EF4444',
            grid: '#334155',
            horizontal: '#06B6D4',
            vertical: '#F472B6'
        };

        // Easing functions
        const Easing = {
            linear: t => t,
            easeIn: t => t * t,
            easeOut: t => t * (2 - t),
            easeInOut: t => t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t,
            easeOutBack: t => {
                const c1 = 1.70158;
                const c3 = c1 + 1;
                return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2);
            },
            easeInCubic: t => t * t * t,
            easeOutCubic: t => 1 - Math.pow(1 - t, 3),
            easeInQuad: t => t * t,
            easeOutQuad: t => t * (2 - t)
        };

        function setup(ctx) {
            return {
                launchX: width * 0.15,
                launchY: height * 0.75,
                initialVelocity: 15,
                angle: 45,
                gravity: 0.5,
                projectileX: 0,
                projectileY: 0,
                velocityX: 0,
                velocityY: 0,
                time: 0,
                isFlying: false,
                trail: [],
                maxTrailLength: 100,
                trajectory: [],
                angleAdjusting: false,
                velocityAdjusting: false,
                particles: [],
                showComponents: true,
                landingX: 0,
                maxHeight: 0,
                flightTime: 0,
                isDragging: false,
                dragTarget: null,
                // Smooth display values for sliders
                displayAngle: 45,
                displayVelocity: 15,
                // Speed control
                speedOptions: [0.25, 0.5, 1, 2, 4],
                currentSpeedIndex: 2  // Default to 1x
            };
        }

        function update(ctx, state, time, vars) {
            // Update speed from state FIRST
            vars.speed = state.speedOptions[state.currentSpeedIndex];

            const dt = 0.016 * vars.speed;

            // Smooth interpolation for display values
            const smoothFactor = 0.2;
            state.displayAngle = state.displayAngle * (1 - smoothFactor) + state.angle * smoothFactor;
            state.displayVelocity = state.displayVelocity * (1 - smoothFactor) + state.initialVelocity * smoothFactor;

            // Clear canvas
            ctx.setFillStyle(COLORS.background);
            ctx.setOpacity(0.15);
            ctx.drawRect(0, 0, width, height);
            ctx.setOpacity(1.0);

            // Draw background
            drawGrid(ctx, 50);
            drawGround(ctx, height * 0.75);

            // Update physics
            if (state.isFlying) {
                // Apply speed multiplier to all physics updates
                state.time += dt;
                state.velocityY += state.gravity * vars.speed;
                state.projectileX += state.velocityX * vars.speed;
                state.projectileY += state.velocityY * vars.speed;

                // Track max height
                if (state.projectileY < state.maxHeight) {
                    state.maxHeight = state.projectileY;
                }

                // Trail
                state.trail.push({ x: state.projectileX, y: state.projectileY, time: state.time });
                if (state.trail.length > state.maxTrailLength) {
                    state.trail.shift();
                }

                // Check landing
                if (state.projectileY >= state.launchY) {
                    state.projectileY = state.launchY;
                    state.isFlying = false;
                    state.landingX = state.projectileX;
                    state.flightTime = state.time;
                    createImpactParticles(state, state.projectileX, state.projectileY);
                }
            } else {
                // Reset for next launch
                state.projectileX = state.launchX;
                state.projectileY = state.launchY;
                state.velocityX = state.initialVelocity * Math.cos(state.angle * Math.PI / 180);
                state.velocityY = -state.initialVelocity * Math.sin(state.angle * Math.PI / 180);

                // Calculate theoretical trajectory
                state.trajectory = calculateTrajectory(state);
            }

            // Update particles
            updateParticles(ctx, state, vars.speed);

            // Draw theoretical trajectory
            if (!state.isFlying) {
                drawTrajectory(ctx, state.trajectory);
            }

            // Draw trail
            drawTrail(ctx, state.trail);

            // Draw launcher
            drawLauncher(ctx, state.launchX, state.launchY, state.angle, state.initialVelocity);

            // Draw projectile
            if (state.isFlying || !state.isFlying) {
                drawProjectile(ctx, state.projectileX, state.projectileY, time / 1000);
            }

            // Draw velocity components
            if (state.showComponents && state.isFlying) {
                drawVelocityComponents(ctx, state.projectileX, state.projectileY,
                    state.velocityX, state.velocityY);
            }

            // Draw decomposed motion views
            drawDecomposedMotion(ctx, state, width * 0.65, height * 0.1);

            // Draw range indicator
            if (!state.isFlying && state.landingX > 0) {
                drawRangeIndicator(ctx, state.launchX, state.landingX, state.launchY);
            }

            // Draw max height indicator
            if (state.maxHeight < state.launchY && state.landingX > 0) {
                drawMaxHeightIndicator(ctx, state.maxHeight, state.launchY);
            }

            // Draw info panel
            const range = Math.abs(state.landingX - state.launchX);
            const maxHeightValue = Math.abs(state.maxHeight - state.launchY);

            drawInfoPanel(ctx, width * 0.02, height * 0.02, [
                `初速度 v₀: ${state.displayVelocity.toFixed(2)} m/s`,
                `角度 θ: ${state.displayAngle.toFixed(1)}°`,
                `水平速度 vₓ: ${state.velocityX.toFixed(2)} m/s`,
                `竖直速度 vᵧ: ${state.velocityY.toFixed(2)} m/s`,
                `飞行时间: ${state.flightTime.toFixed(2)} s`,
                `射程: ${range.toFixed(1)} m`,
                `最大高度: ${maxHeightValue.toFixed(1)} m`
            ]);

            // Draw control panel
            drawControlPanel(ctx, state, width * 0.02, height * 0.45);

            // Draw formulas
            drawFormulas(ctx, width * 0.65, height * 0.55);

            // Draw speed control
            drawSpeedControl(ctx, state, width * 0.65, height * 0.75);

            // Draw title
            drawTitle(ctx, width * 0.5, height * 0.05, '抛体运动模拟');

            // Draw angle arc
            drawAngleArc(ctx, state.launchX, state.launchY, state.angle);
        }

        // Helper functions (12+ required)

        function drawGrid(ctx, spacing) {
            ctx.setStrokeStyle(COLORS.grid);
            ctx.setOpacity(0.08);
            ctx.setLineWidth(1);

            for (let x = 0; x < width; x += spacing) {
                ctx.drawLine(x, 0, x, height);
            }
            for (let y = 0; y < height; y += spacing) {
                ctx.drawLine(0, y, width, y);
            }
            ctx.setOpacity(1.0);
        }

        function drawGround(ctx, y) {
            // Ground surface
            ctx.setFillStyle(COLORS.grid);
            ctx.setOpacity(0.2);
            ctx.drawRect(0, y, width, height - y);
            ctx.setOpacity(1.0);

            // Ground line
            ctx.setStrokeStyle(COLORS.success);
            ctx.setLineWidth(3);
            ctx.setGlow(COLORS.success, 10);
            ctx.drawLine(0, y, width, y);
            ctx.setGlow(null, 0);

            // Hatching pattern
            ctx.setStrokeStyle(COLORS.grid);
            ctx.setOpacity(0.3);
            ctx.setLineWidth(1);
            for (let x = 0; x < width; x += 20) {
                ctx.drawLine(x, y, x - 10, y + 20);
            }
            ctx.setOpacity(1.0);
        }

        function drawLauncher(ctx, x, y, angle, velocity) {
            const launcherLength = 60;
            const angleRad = angle * Math.PI / 180;
            const endX = x + launcherLength * Math.cos(angleRad);
            const endY = y - launcherLength * Math.sin(angleRad);

            // Base platform
            ctx.setFillStyle(COLORS.grid);
            ctx.drawRect(x - 30, y, 60, 15);

            // Launcher barrel
            ctx.setStrokeStyle(COLORS.accent);
            ctx.setLineWidth(8);
            ctx.setGlow(COLORS.accent, 15);
            ctx.drawLine(x, y, endX, endY);
            ctx.setGlow(null, 0);

            // Tip
            ctx.setFillStyle(COLORS.secondary);
            ctx.setGlow(COLORS.secondary, 10);
            ctx.drawCircle(endX, endY, 6);
            ctx.setGlow(null, 0);

            // Base
            ctx.setFillStyle(COLORS.accent);
            ctx.drawCircle(x, y, 12);
        }

        function drawProjectile(ctx, x, y, t) {
            // Outer glow
            ctx.setFillStyle(COLORS.secondary);
            ctx.setGlow(COLORS.secondary, 25);
            ctx.drawCircle(x, y, 18);
            ctx.setGlow(null, 0);

            // Main body
            ctx.setFillStyle(COLORS.secondary);
            ctx.drawCircle(x, y, 12);

            // Core pulse
            const pulseSize = 6 + Math.sin(t * 6) * 2;
            ctx.setFillStyle('#FFFFFF');
            ctx.drawCircle(x, y, pulseSize);
        }

        function drawTrajectory(ctx, trajectory) {
            if (trajectory.length < 2) return;

            ctx.setStrokeStyle(COLORS.primary);
            ctx.setOpacity(0.3);
            ctx.setLineWidth(2);
            ctx.setLineDash([5, 5]);

            for (let i = 0; i < trajectory.length - 1; i++) {
                ctx.drawLine(trajectory[i].x, trajectory[i].y,
                    trajectory[i + 1].x, trajectory[i + 1].y);
            }

            ctx.setLineDash([]);
            ctx.setOpacity(1.0);
        }

        function drawTrail(ctx, trail) {
            for (let i = 0; i < trail.length; i++) {
                const progress = i / trail.length;
                const opacity = Easing.easeOut(progress) * 0.7;
                const size = Easing.easeOut(progress) * 6 + 2;

                ctx.setFillStyle(COLORS.secondary);
                ctx.setOpacity(opacity);
                ctx.drawCircle(trail[i].x, trail[i].y, size);
            }
            ctx.setOpacity(1.0);
        }

        function drawVelocityComponents(ctx, x, y, vx, vy) {
            const scale = 3;

            // Horizontal component (cyan)
            ctx.setStrokeStyle(COLORS.horizontal);
            ctx.setLineWidth(3);
            ctx.setGlow(COLORS.horizontal, 8);
            ctx.drawLine(x, y, x + vx * scale, y);
            ctx.setGlow(null, 0);
            drawArrowhead(ctx, x + vx * scale, y, 0, COLORS.horizontal);

            ctx.setFillStyle(COLORS.horizontal);
            ctx.setFontSize(14);
            ctx.drawText('vₓ', x + vx * scale / 2, y - 10);

            // Vertical component (pink)
            ctx.setStrokeStyle(COLORS.vertical);
            ctx.setLineWidth(3);
            ctx.setGlow(COLORS.vertical, 8);
            ctx.drawLine(x, y, x, y + vy * scale);
            ctx.setGlow(null, 0);
            drawArrowhead(ctx, x, y + vy * scale, Math.PI / 2 * Math.sign(vy), COLORS.vertical);

            ctx.setFillStyle(COLORS.vertical);
            ctx.setFontSize(14);
            ctx.drawText('vᵧ', x + 15, y + vy * scale / 2);

            // Resultant velocity
            ctx.setStrokeStyle(COLORS.success);
            ctx.setLineWidth(3);
            ctx.setGlow(COLORS.success, 8);
            ctx.drawLine(x, y, x + vx * scale, y + vy * scale);
            ctx.setGlow(null, 0);

            const angle = Math.atan2(vy, vx);
            drawArrowhead(ctx, x + vx * scale, y + vy * scale, angle, COLORS.success);

            ctx.setFillStyle(COLORS.success);
            ctx.setFontSize(14);
            ctx.drawText('v', x + vx * scale / 2 + 15, y + vy * scale / 2 - 10);
        }

        function drawArrowhead(ctx, x, y, angle, color) {
            const size = 10;
            ctx.setFillStyle(color);
            ctx.drawPath([
                { x: x, y: y },
                { x: x - size * Math.cos(angle - Math.PI / 6),
                  y: y - size * Math.sin(angle - Math.PI / 6) },
                { x: x - size * Math.cos(angle + Math.PI / 6),
                  y: y - size * Math.sin(angle + Math.PI / 6) }
            ], true);
        }

        function drawDecomposedMotion(ctx, state, x, y) {
            const panelWidth = width * 0.3;
            const panelHeight = height * 0.35;

            // Panel background
            ctx.setFillStyle(COLORS.background);
            ctx.setOpacity(0.9);
            ctx.drawRect(x, y, panelWidth, panelHeight);
            ctx.setOpacity(1.0);

            // Border
            ctx.setStrokeStyle(COLORS.primary);
            ctx.setLineWidth(2);
            ctx.setGlow(COLORS.primary, 8);
            ctx.drawLine(x, y, x + panelWidth, y);
            ctx.drawLine(x + panelWidth, y, x + panelWidth, y + panelHeight);
            ctx.drawLine(x + panelWidth, y + panelHeight, x, y + panelHeight);
            ctx.drawLine(x, y + panelHeight, x, y);
            ctx.setGlow(null, 0);

            // Title
            ctx.setFillStyle(COLORS.text);
            ctx.setFontSize(16);
            ctx.drawText('分解运动', x + 10, y + 25);

            // Horizontal motion
            const hMotionY = y + 70;
            ctx.setFillStyle(COLORS.text);
            ctx.setFontSize(14);
            ctx.drawText('水平运动 (匀速):', x + 10, hMotionY);

            ctx.setStrokeStyle(COLORS.horizontal);
            ctx.setLineWidth(2);
            ctx.drawLine(x + 20, hMotionY + 20, x + panelWidth - 20, hMotionY + 20);

            if (state.isFlying) {
                const progress = (state.projectileX - state.launchX) / (panelWidth - 40);
                const dotX = x + 20 + Math.min(progress * (panelWidth - 40), panelWidth - 40);
                ctx.setFillStyle(COLORS.horizontal);
                ctx.setGlow(COLORS.horizontal, 15);
                ctx.drawCircle(dotX, hMotionY + 20, 8);
                ctx.setGlow(null, 0);
            }

            // Vertical motion
            const vMotionY = y + 150;
            ctx.setFillStyle(COLORS.text);
            ctx.setFontSize(14);
            ctx.drawText('竖直运动 (加速):', x + 10, vMotionY);

            const vLineX = x + panelWidth / 2;
            ctx.setStrokeStyle(COLORS.vertical);
            ctx.setLineWidth(2);
            ctx.drawLine(vLineX, vMotionY + 20, vLineX, vMotionY + 120);

            if (state.isFlying) {
                const relativeY = state.projectileY - state.launchY;
                const maxDrop = 100;
                const dotY = vMotionY + 20 + Math.min(Math.max(relativeY, -maxDrop), maxDrop);
                ctx.setFillStyle(COLORS.vertical);
                ctx.setGlow(COLORS.vertical, 15);
                ctx.drawCircle(vLineX, dotY, 8);
                ctx.setGlow(null, 0);
            }

            // Ground reference
            ctx.setStrokeStyle(COLORS.success);
            ctx.setLineWidth(2);
            ctx.setLineDash([5, 5]);
            ctx.drawLine(vLineX - 30, vMotionY + 20, vLineX + 30, vMotionY + 20);
            ctx.setLineDash([]);
        }

        function drawRangeIndicator(ctx, x1, x2, y) {
            ctx.setStrokeStyle(COLORS.secondary);
            ctx.setLineWidth(2);
            ctx.setOpacity(0.6);
            ctx.drawLine(x1, y + 30, x2, y + 30);

            // Arrows
            drawArrowhead(ctx, x1, y + 30, Math.PI, COLORS.secondary);
            drawArrowhead(ctx, x2, y + 30, 0, COLORS.secondary);

            ctx.setOpacity(1.0);

            // Label
            const range = Math.abs(x2 - x1);
            ctx.setFillStyle(COLORS.secondary);
            ctx.setFontSize(16);
            ctx.drawText(`R = ${range.toFixed(1)} m`, (x1 + x2) / 2 - 40, y + 50);
        }

        function drawMaxHeightIndicator(ctx, maxY, groundY) {
            const x = width * 0.1;

            ctx.setStrokeStyle(COLORS.danger);
            ctx.setLineWidth(2);
            ctx.setOpacity(0.6);
            ctx.drawLine(x, maxY, x, groundY);

            // Arrows
            drawArrowhead(ctx, x, maxY, -Math.PI / 2, COLORS.danger);
            drawArrowhead(ctx, x, groundY, Math.PI / 2, COLORS.danger);

            ctx.setOpacity(1.0);

            // Label
            const height = Math.abs(maxY - groundY);
            ctx.setFillStyle(COLORS.danger);
            ctx.setFontSize(16);
            ctx.drawText(`H = ${height.toFixed(1)} m`, x + 15, (maxY + groundY) / 2);

            // Max height line
            ctx.setStrokeStyle(COLORS.danger);
            ctx.setOpacity(0.3);
            ctx.setLineDash([5, 5]);
            ctx.drawLine(x - 20, maxY, width * 0.6, maxY);
            ctx.setLineDash([]);
            ctx.setOpacity(1.0);
        }

        function drawInfoPanel(ctx, x, y, lines) {
            const padding = 15;
            const lineHeight = 25;
            const panelWidth = width * 0.25;
            const panelHeight = lines.length * lineHeight + padding * 2;

            // Panel background
            ctx.setFillStyle(COLORS.background);
            ctx.setOpacity(0.85);
            ctx.drawRect(x, y, panelWidth, panelHeight);
            ctx.setOpacity(1.0);

            // Border
            ctx.setStrokeStyle(COLORS.primary);
            ctx.setLineWidth(2);
            ctx.setGlow(COLORS.primary, 8);
            ctx.drawLine(x, y, x + panelWidth, y);
            ctx.drawLine(x + panelWidth, y, x + panelWidth, y + panelHeight);
            ctx.drawLine(x + panelWidth, y + panelHeight, x, y + panelHeight);
            ctx.drawLine(x, y + panelHeight, x, y);
            ctx.setGlow(null, 0);

            // Text
            ctx.setFillStyle(COLORS.text);
            ctx.setFontSize(15);
            lines.forEach((line, i) => {
                ctx.drawText(line, x + padding, y + padding + (i + 1) * lineHeight);
            });
        }

        function drawControlPanel(ctx, state, x, y) {
            const padding = 15;
            const panelWidth = width * 0.25;
            const panelHeight = height * 0.25;

            // Panel background
            ctx.setFillStyle(COLORS.background);
            ctx.setOpacity(0.85);
            ctx.drawRect(x, y, panelWidth, panelHeight);
            ctx.setOpacity(1.0);

            // Border
            ctx.setStrokeStyle(COLORS.secondary);
            ctx.setLineWidth(2);
            ctx.drawLine(x, y, x + panelWidth, y);
            ctx.drawLine(x + panelWidth, y, x + panelWidth, y + panelHeight);
            ctx.drawLine(x + panelWidth, y + panelHeight, x, y + panelHeight);
            ctx.drawLine(x, y + panelHeight, x, y);

            // Title
            ctx.setFillStyle(COLORS.text);
            ctx.setFontSize(16);
            ctx.drawText('控制面板', x + padding, y + padding + 20);

            // Angle slider
            ctx.setFontSize(14);
            ctx.drawText(`角度: ${state.displayAngle.toFixed(1)}°`, x + padding, y + padding + 50);
            drawSlider(ctx, x + padding, y + padding + 60, panelWidth - padding * 2, state.displayAngle, 0, 90, COLORS.accent);

            // Velocity slider
            ctx.drawText(`初速度: ${state.displayVelocity.toFixed(1)} m/s`, x + padding, y + padding + 100);
            drawSlider(ctx, x + padding, y + padding + 110, panelWidth - padding * 2, state.displayVelocity, 5, 25, COLORS.primary);

            // Launch button
            const buttonY = y + padding + 150;
            drawButton(ctx, x + padding, buttonY, panelWidth - padding * 2, 35,
                state.isFlying ? '飞行中...' : '发射', !state.isFlying);
        }

        function drawSlider(ctx, x, y, w, value, min, max, color) {
            // Track
            ctx.setStrokeStyle(COLORS.grid);
            ctx.setLineWidth(4);
            ctx.drawLine(x, y, x + w, y);

            // Progress
            const progress = (value - min) / (max - min);
            ctx.setStrokeStyle(color);
            ctx.setLineWidth(4);
            ctx.drawLine(x, y, x + w * progress, y);

            // Handle
            ctx.setFillStyle(color);
            ctx.setGlow(color, 15);
            ctx.drawCircle(x + w * progress, y, 8);
            ctx.setGlow(null, 0);
        }

        function drawButton(ctx, x, y, w, h, text, enabled) {
            // Background
            ctx.setFillStyle(enabled ? COLORS.success : COLORS.grid);
            ctx.setOpacity(enabled ? 1.0 : 0.5);
            ctx.drawRect(x, y, w, h);
            ctx.setOpacity(1.0);

            // Border
            ctx.setStrokeStyle(enabled ? COLORS.success : COLORS.grid);
            ctx.setLineWidth(2);
            if (enabled) ctx.setGlow(COLORS.success, 10);
            ctx.drawLine(x, y, x + w, y);
            ctx.drawLine(x + w, y, x + w, y + h);
            ctx.drawLine(x + w, y + h, x, y + h);
            ctx.drawLine(x, y + h, x, y);
            ctx.setGlow(null, 0);

            // Text
            ctx.setFillStyle(COLORS.text);
            ctx.setFontSize(16);
            ctx.drawText(text, x + w / 2 - text.length * 4, y + h / 2 + 5);
        }

        function drawFormulas(ctx, x, y) {
            const panelWidth = width * 0.3;
            const panelHeight = height * 0.18;

            // Panel background
            ctx.setFillStyle(COLORS.background);
            ctx.setOpacity(0.9);
            ctx.drawRect(x, y, panelWidth, panelHeight);
            ctx.setOpacity(1.0);

            // Border
            ctx.setStrokeStyle(COLORS.accent);
            ctx.setLineWidth(2);
            ctx.drawLine(x, y, x + panelWidth, y);
            ctx.drawLine(x + panelWidth, y, x + panelWidth, y + panelHeight);
            ctx.drawLine(x + panelWidth, y + panelHeight, x, y + panelHeight);
            ctx.drawLine(x, y + panelHeight, x, y);

            // Formulas
            ctx.setFillStyle(COLORS.text);
            ctx.setFontSize(14);
            ctx.drawText('运动方程:', x + 15, y + 25);
            ctx.setFontSize(12);
            ctx.drawText('x = v₀·cos(θ)·t', x + 15, y + 50);
            ctx.drawText('y = v₀·sin(θ)·t - ½gt²', x + 15, y + 70);
            ctx.drawText('R = v₀²·sin(2θ)/g', x + 15, y + 95);
            ctx.drawText('H = v₀²·sin²(θ)/(2g)', x + 15, y + 115);
        }

        function drawSpeedControl(ctx, state, x, y) {
            const panelWidth = width * 0.3;
            const panelHeight = height * 0.12;

            // Panel background
            ctx.setFillStyle(COLORS.background);
            ctx.setOpacity(0.9);
            ctx.drawRect(x, y, panelWidth, panelHeight);
            ctx.setOpacity(1.0);

            // Border
            ctx.setStrokeStyle(COLORS.success);
            ctx.setLineWidth(2);
            ctx.drawLine(x, y, x + panelWidth, y);
            ctx.drawLine(x + panelWidth, y, x + panelWidth, y + panelHeight);
            ctx.drawLine(x + panelWidth, y + panelHeight, x, y + panelHeight);
            ctx.drawLine(x, y + panelHeight, x, y);

            // Title
            ctx.setFillStyle(COLORS.text);
            ctx.setFontSize(14);
            ctx.drawText('播放速度:', x + 15, y + 25);

            // Speed buttons
            const buttonWidth = 50;
            const buttonHeight = 30;
            const buttonSpacing = 8;
            const startX = x + 15;
            const buttonY = y + 40;

            state.speedOptions.forEach((speed, index) => {
                const buttonX = startX + index * (buttonWidth + buttonSpacing);
                const isActive = state.currentSpeedIndex === index;

                // Button background
                ctx.setFillStyle(isActive ? COLORS.success : COLORS.grid);
                ctx.setOpacity(isActive ? 1.0 : 0.5);
                ctx.drawRect(buttonX, buttonY, buttonWidth, buttonHeight);
                ctx.setOpacity(1.0);

                // Button border
                ctx.setStrokeStyle(isActive ? COLORS.success : COLORS.grid);
                ctx.setLineWidth(2);
                if (isActive) ctx.setGlow(COLORS.success, 10);
                ctx.drawLine(buttonX, buttonY, buttonX + buttonWidth, buttonY);
                ctx.drawLine(buttonX + buttonWidth, buttonY, buttonX + buttonWidth, buttonY + buttonHeight);
                ctx.drawLine(buttonX + buttonWidth, buttonY + buttonHeight, buttonX, buttonY + buttonHeight);
                ctx.drawLine(buttonX, buttonY + buttonHeight, buttonX, buttonY);
                ctx.setGlow(null, 0);

                // Button text
                ctx.setFillStyle(COLORS.text);
                ctx.setFontSize(13);
                const label = speed === 1 ? '1x' : speed < 1 ? `${speed}x` : `${speed}x`;
                const textOffset = label.length === 2 ? 13 : label.length === 3 ? 9 : 16;
                ctx.drawText(label, buttonX + textOffset, buttonY + buttonHeight / 2 + 5);
            });
        }

        function drawTitle(ctx, x, y, text) {
            ctx.setFillStyle(COLORS.text);
            ctx.setFontSize(32);
            ctx.setGlow(COLORS.secondary, 15);
            ctx.drawText(text, x - text.length * 8, y);
            ctx.setGlow(null, 0);
        }

        function drawAngleArc(ctx, x, y, angle) {
            const radius = 40;
            const angleRad = angle * Math.PI / 180;

            ctx.setStrokeStyle(COLORS.accent);
            ctx.setLineWidth(2);
            ctx.setOpacity(0.6);

            const steps = 20;
            for (let i = 0; i < steps; i++) {
                const a1 = (i / steps) * angleRad;
                const a2 = ((i + 1) / steps) * angleRad;
                const x1 = x + radius * Math.cos(a1);
                const y1 = y - radius * Math.sin(a1);
                const x2 = x + radius * Math.cos(a2);
                const y2 = y - radius * Math.sin(a2);
                ctx.drawLine(x1, y1, x2, y2);
            }

            ctx.setOpacity(1.0);

            // Label
            ctx.setFillStyle(COLORS.accent);
            ctx.setFontSize(14);
            ctx.drawText(`θ`, x + radius * 1.3, y - radius * 0.3);
        }

        function calculateTrajectory(state) {
            const trajectory = [];
            const steps = 100;
            const vx = state.initialVelocity * Math.cos(state.angle * Math.PI / 180);
            const vy = -state.initialVelocity * Math.sin(state.angle * Math.PI / 180);

            for (let i = 0; i <= steps; i++) {
                const t = i * 0.1;
                const x = state.launchX + vx * t;
                const y = state.launchY + vy * t + 0.5 * state.gravity * t * t;

                if (y >= state.launchY) break;
                trajectory.push({ x, y });
            }

            return trajectory;
        }

        function createImpactParticles(state, x, y) {
            for (let i = 0; i < 20; i++) {
                const angle = Math.random() * Math.PI;
                const speed = Math.random() * 3 + 1;
                state.particles.push({
                    x: x,
                    y: y,
                    vx: Math.cos(angle) * speed,
                    vy: Math.sin(angle) * speed - 2,
                    life: 1.0,
                    size: Math.random() * 4 + 2,
                    color: Math.random() > 0.5 ? COLORS.secondary : COLORS.danger
                });
            }
        }

        function updateParticles(ctx, state, speed) {
            state.particles = state.particles.filter(p => {
                p.x += p.vx * speed;
                p.y += p.vy * speed;
                p.vy += 0.2 * speed; // gravity
                p.life -= 0.02 * speed;

                if (p.life > 0) {
                    ctx.setFillStyle(p.color);
                    ctx.setOpacity(p.life * 0.8);
                    ctx.drawCircle(p.x, p.y, p.size * p.life);
                    return true;
                }
                return false;
            });
            ctx.setOpacity(1.0);
        }

        // Mock context implementation
        function createMockContext(canvas) {
            const realCtx = canvas.getContext('2d');

            const ctx = {
                setFillStyle(color) { realCtx.fillStyle = color; },
                setStrokeStyle(color) { realCtx.strokeStyle = color; },
                setLineWidth(width) { realCtx.lineWidth = width; },
                setOpacity(alpha) { realCtx.globalAlpha = alpha; },
                setFontSize(size) { realCtx.font = `${size}px 'Segoe UI', sans-serif`; },
                setLineDash(segments) { realCtx.setLineDash(segments); },
                setGlow(color, blur) {
                    if (color) {
                        realCtx.shadowColor = color;
                        realCtx.shadowBlur = blur;
                    } else {
                        realCtx.shadowColor = 'transparent';
                        realCtx.shadowBlur = 0;
                    }
                },
                drawRect(x, y, w, h) { realCtx.fillRect(x, y, w, h); },
                drawCircle(x, y, radius) {
                    realCtx.beginPath();
                    realCtx.arc(x, y, radius, 0, Math.PI * 2);
                    realCtx.fill();
                },
                drawLine(x1, y1, x2, y2) {
                    realCtx.beginPath();
                    realCtx.moveTo(x1, y1);
                    realCtx.lineTo(x2, y2);
                    realCtx.stroke();
                },
                drawText(text, x, y) { realCtx.fillText(text, x, y); },
                drawPath(points, close = false) {
                    if (points.length === 0) return;
                    realCtx.beginPath();
                    realCtx.moveTo(points[0].x, points[0].y);
                    for (let i = 1; i < points.length; i++) {
                        realCtx.lineTo(points[i].x, points[i].y);
                    }
                    if (close) realCtx.closePath();
                    realCtx.fill();
                },
                onClick(callback) {
                    canvas.addEventListener('click', (e) => {
                        const rect = canvas.getBoundingClientRect();
                        callback(e.clientX - rect.left, e.clientY - rect.top);
                    });
                },
                onDrag(callback) {
                    let dragging = false;
                    canvas.addEventListener('mousedown', (e) => {
                        dragging = true;
                        const rect = canvas.getBoundingClientRect();
                        callback(e.clientX - rect.left, e.clientY - rect.top, 'start');
                    });
                    canvas.addEventListener('mousemove', (e) => {
                        if (dragging) {
                            const rect = canvas.getBoundingClientRect();
                            callback(e.clientX - rect.left, e.clientY - rect.top, 'move');
                        }
                    });
                    canvas.addEventListener('mouseup', () => {
                        if (dragging) {
                            dragging = false;
                            callback(0, 0, 'end');
                        }
                    });
                }
            };

            return ctx;
        }

        // Initialize
        const ctx = createMockContext(canvas);
        const state = setup(ctx);
        const vars = { speed: 1.0 };
        let startTime = Date.now();

        // Setup click interaction
        ctx.onClick((x, y) => {
            const controlX = width * 0.02;
            const controlY = height * 0.45;
            const panelWidth = width * 0.25;
            const padding = 15;

            // Check launch button
            const buttonY = controlY + padding + 150;
            if (x >= controlX + padding && x <= controlX + panelWidth - padding &&
                y >= buttonY && y <= buttonY + 35 && !state.isFlying) {
                state.isFlying = true;
                state.time = 0;
                state.trail = [];
                state.maxHeight = state.launchY;
                state.landingX = 0;
                state.flightTime = 0;
                state.particles = [];
            }

            // Check speed control buttons
            const speedPanelX = width * 0.65;
            const speedPanelY = height * 0.75;
            const buttonWidth = 50;
            const buttonHeight = 30;
            const buttonSpacing = 8;
            const startX = speedPanelX + 15;
            const speedButtonY = speedPanelY + 40;

            state.speedOptions.forEach((speed, index) => {
                const buttonX = startX + index * (buttonWidth + buttonSpacing);
                if (x >= buttonX && x <= buttonX + buttonWidth &&
                    y >= speedButtonY && y <= speedButtonY + buttonHeight) {
                    state.currentSpeedIndex = index;
                }
            });
        });

        // Setup drag interaction for sliders
        ctx.onDrag((x, y, phase) => {
            const controlX = width * 0.02;
            const controlY = height * 0.45;
            const panelWidth = width * 0.25;
            const padding = 15;
            const sliderWidth = panelWidth - padding * 2;

            if (phase === 'start') {
                const angleSliderY = controlY + padding + 60;
                const velSliderY = controlY + padding + 110;

                // Check angle slider
                if (x >= controlX + padding && x <= controlX + panelWidth - padding &&
                    y >= angleSliderY - 10 && y <= angleSliderY + 10) {
                    state.isDragging = true;
                    state.dragTarget = 'angle';
                }
                // Check velocity slider
                else if (x >= controlX + padding && x <= controlX + panelWidth - padding &&
                    y >= velSliderY - 10 && y <= velSliderY + 10) {
                    state.isDragging = true;
                    state.dragTarget = 'velocity';
                }
            } else if (phase === 'move' && state.isDragging) {
                const progress = Math.max(0, Math.min(1, (x - (controlX + padding)) / sliderWidth));

                if (state.dragTarget === 'angle') {
                    state.angle = 0 + progress * 90;
                } else if (state.dragTarget === 'velocity') {
                    state.initialVelocity = 5 + progress * 20;
                }
            } else if (phase === 'end') {
                state.isDragging = false;
                state.dragTarget = null;
            }
        });

        // Animation loop
        function animate() {
            const time = Date.now() - startTime;
            update(ctx, state, time, vars);
            requestAnimationFrame(animate);
        }

        animate();
    </script>
</body>
</html>$HTML$,
 75,
 265,
 962,
 false,
 0,
 NOW(),
 '{"name": "抛体运动", "description": "模拟抛体运动轨迹，展示初速度、角度对射程和高度的影响", "difficulty": "medium", "render_mode": "html"}');


-- [3/24] 弹簧振子 (physics, 75分)
INSERT INTO simulator_templates
(subject, topic, code, quality_score, visual_elements, line_count, has_setup_update, variable_count, created_at, metadata)
VALUES
('physics',
 '弹簧振子',
 $HTML$<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>弹簧振子 - Spring Oscillator</title>
    <style>
        body {
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background: #0f172a;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        canvas {
            border: 1px solid #334155;
            box-shadow: 0 0 30px rgba(139, 92, 246, 0.3);
        }
    </style>
</head>
<body>
    <canvas id="canvas" width="1200" height="800"></canvas>
    <script>
        const canvas = document.getElementById('canvas');
        const width = canvas.width;
        const height = canvas.height;

        // 学科配色
        const COLORS = {
            primary: '#3B82F6',
            secondary: '#F59E0B',
            accent: '#8B5CF6',
            background: '#1E293B',
            text: '#F1F5F9',
            success: '#10B981',
            danger: '#EF4444',
            grid: '#334155',
            spring: '#06B6D4'
        };

        // Easing functions
        const Easing = {
            linear: t => t,
            easeIn: t => t * t,
            easeOut: t => t * (2 - t),
            easeInOut: t => t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t,
            easeOutBack: t => {
                const c1 = 1.70158;
                const c3 = c1 + 1;
                return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2);
            },
            easeInCubic: t => t * t * t,
            easeOutCubic: t => 1 - Math.pow(1 - t, 3),
            easeInElastic: t => {
                const c4 = (2 * Math.PI) / 3;
                return t === 0 ? 0 : t === 1 ? 1 : -Math.pow(2, 10 * t - 10) * Math.sin((t * 10 - 10.75) * c4);
            }
        };

        function setup(ctx) {
            return {
                equilibriumY: height * 0.3,
                displacement: 0,
                velocity: 0,
                mass: 3.0,  // Increased mass for slower oscillation
                springConstant: 0.15,  // Reduced spring constant for slower oscillation
                damping: 0.015,  // Reduced damping for longer oscillation
                fixedPointX: width * 0.5,
                fixedPointY: height * 0.1,
                isDragging: false,
                amplitude: height * 0.15,
                time: 0,
                energyHistory: [],
                maxEnergyHistory: 150,
                showEnergy: true,
                oscillationCount: 0,
                lastDisplacement: 0,
                maxEnergyScale: 10, // Smooth maximum energy for bar scaling
                // Smooth display values for animation (higher smoothing factor)
                displayDisplacement: 0,
                displayVelocity: 0,
                displayKineticEnergy: 0,
                displayPotentialEnergy: 0,
                displayTotalEnergy: 0
            };
        }

        function update(ctx, state, time, vars) {
            const dt = 0.016 * vars.speed; // ~60fps
            state.time += dt;

            // Clear canvas with fade
            ctx.setFillStyle(COLORS.background);
            ctx.setOpacity(0.2);
            ctx.drawRect(0, 0, width, height);
            ctx.setOpacity(1.0);

            // Draw background grid
            drawGrid(ctx, 50);

            // Update physics if not dragging
            if (!state.isDragging) {
                const springForce = -state.springConstant * state.displacement;
                const dampingForce = -state.damping * state.velocity;
                const totalForce = springForce + dampingForce;
                const acceleration = totalForce / state.mass;

                state.velocity += acceleration;
                state.displacement += state.velocity;

                // Count oscillations
                if (state.lastDisplacement * state.displacement < 0) {
                    state.oscillationCount++;
                }
                state.lastDisplacement = state.displacement;
            }

            // Smooth interpolation for display values (lerp with higher factor for ultra-smooth animation)
            const smoothFactor = 0.25;  // Increased from 0.15 for more smoothing
            state.displayDisplacement = state.displayDisplacement * (1 - smoothFactor) + state.displacement * smoothFactor;
            state.displayVelocity = state.displayVelocity * (1 - smoothFactor) + state.velocity * smoothFactor;

            const massY = state.equilibriumY + state.displayDisplacement;

            // Calculate energies using actual values
            const kineticEnergy = 0.5 * state.mass * state.velocity * state.velocity;
            const potentialEnergy = 0.5 * state.springConstant * state.displacement * state.displacement;
            const totalEnergy = kineticEnergy + potentialEnergy;

            // Smooth display energies (higher smoothing for energy bars)
            const energySmoothFactor = 0.2;  // Slightly higher smoothing for energy
            state.displayKineticEnergy = state.displayKineticEnergy * (1 - energySmoothFactor) + kineticEnergy * energySmoothFactor;
            state.displayPotentialEnergy = state.displayPotentialEnergy * (1 - energySmoothFactor) + potentialEnergy * energySmoothFactor;
            state.displayTotalEnergy = state.displayTotalEnergy * (1 - energySmoothFactor) + totalEnergy * energySmoothFactor;

            // Smoothly update max energy scale for stable bar visualization
            if (totalEnergy > state.maxEnergyScale) {
                state.maxEnergyScale = state.maxEnergyScale * 0.85 + totalEnergy * 0.15;
            } else {
                // Very slowly decay the max scale towards current total energy
                state.maxEnergyScale = state.maxEnergyScale * 0.998 + totalEnergy * 0.002;
            }
            // Ensure minimum scale
            state.maxEnergyScale = Math.max(state.maxEnergyScale, 1);

            // Store energy history
            state.energyHistory.push({
                kinetic: kineticEnergy,
                potential: potentialEnergy,
                total: totalEnergy,
                time: state.time
            });
            if (state.energyHistory.length > state.maxEnergyHistory) {
                state.energyHistory.shift();
            }

            // Draw fixed support
            drawFixedSupport(ctx, state.fixedPointX, state.fixedPointY);

            // Draw spring
            drawSpring(ctx, state.fixedPointX, state.fixedPointY, state.fixedPointX, massY, 20, 15);

            // Draw mass
            drawMass(ctx, state.fixedPointX, massY, state.mass, state.time);

            // Draw equilibrium line
            drawEquilibriumLine(ctx, state.equilibriumY);

            // Draw velocity vector (always show, even if small)
            drawVelocityVector(ctx, state.fixedPointX, massY, state.displayVelocity);

            // Draw force vectors
            const springForce = -state.springConstant * state.displayDisplacement;
            drawForceVector(ctx, state.fixedPointX, massY, springForce, COLORS.danger, 'F');

            // Draw energy graphs with smooth display values
            if (state.showEnergy) {
                drawEnergyGraph(ctx, state.energyHistory, width * 0.65, height * 0.15, width * 0.3, height * 0.25);
                drawEnergyBars(ctx, state.displayKineticEnergy, state.displayPotentialEnergy, state.displayTotalEnergy, state.maxEnergyScale, width * 0.65, height * 0.5, width * 0.3, height * 0.3);
            }

            // Draw info panel with smooth display values
            drawInfoPanel(ctx, width * 0.02, height * 0.02, [
                `位移 x: ${state.displayDisplacement.toFixed(2)} px`,
                `速度 v: ${state.displayVelocity.toFixed(2)} px/s`,
                `动能 Ek: ${state.displayKineticEnergy.toFixed(2)} J`,
                `势能 Ep: ${state.displayPotentialEnergy.toFixed(2)} J`,
                `总能量 E: ${state.displayTotalEnergy.toFixed(2)} J`,
                `振荡次数: ${Math.floor(state.oscillationCount / 2)}`
            ]);

            // Draw parameters panel
            drawParametersPanel(ctx, width * 0.02, height * 0.45, [
                `质量 m: ${state.mass.toFixed(1)} kg`,
                `弹簧常数 k: ${state.springConstant.toFixed(2)} N/m`,
                `阻尼系数 b: ${state.damping.toFixed(3)} N·s/m`,
                `周期 T: ${(2 * Math.PI * Math.sqrt(state.mass / state.springConstant)).toFixed(2)} s`
            ]);

            // Draw control instructions
            drawControlPanel(ctx, width * 0.02, height * 0.75);

            // Draw title
            drawTitle(ctx, width * 0.5, height * 0.05, '弹簧振子模拟');

            // Draw decorative particles (use smooth velocity)
            drawDecorativeParticles(ctx, state.fixedPointX, massY, state.time, state.displayVelocity);

            // Draw displacement indicator
            drawDisplacementIndicator(ctx, width * 0.12, state.equilibriumY, width * 0.12, massY);
        }

        // Helper functions (12+ required)

        function drawGrid(ctx, spacing) {
            ctx.setStrokeStyle(COLORS.grid);
            ctx.setOpacity(0.08);
            ctx.setLineWidth(1);

            for (let x = 0; x < width; x += spacing) {
                ctx.drawLine(x, 0, x, height);
            }
            for (let y = 0; y < height; y += spacing) {
                ctx.drawLine(0, y, width, y);
            }
            ctx.setOpacity(1.0);
        }

        function drawFixedSupport(ctx, x, y) {
            const supportWidth = width * 0.15;
            const supportHeight = 20;

            // Support bar
            ctx.setFillStyle(COLORS.grid);
            ctx.setGlow(COLORS.primary, 10);
            ctx.drawRect(x - supportWidth / 2, y - supportHeight / 2, supportWidth, supportHeight);
            ctx.setGlow(null, 0);

            // Hatching pattern
            ctx.setStrokeStyle(COLORS.text);
            ctx.setOpacity(0.3);
            ctx.setLineWidth(1);
            for (let i = 0; i < supportWidth; i += 10) {
                const startX = x - supportWidth / 2 + i;
                ctx.drawLine(startX, y + supportHeight / 2, startX - 8, y + supportHeight / 2 + 15);
            }
            ctx.setOpacity(1.0);
        }

        function drawSpring(ctx, x1, y1, x2, y2, coils, amplitude) {
            const segments = coils * 4;
            const dx = x2 - x1;
            const dy = y2 - y1;
            const length = Math.sqrt(dx * dx + dy * dy);

            ctx.setStrokeStyle(COLORS.spring);
            ctx.setLineWidth(3);
            ctx.setGlow(COLORS.spring, 8);

            for (let i = 0; i < segments; i++) {
                const t1 = i / segments;
                const t2 = (i + 1) / segments;

                const offset1 = Math.sin(t1 * coils * Math.PI * 2) * amplitude;
                const offset2 = Math.sin(t2 * coils * Math.PI * 2) * amplitude;

                const px1 = x1 + dx * t1 + offset1;
                const py1 = y1 + dy * t1;
                const px2 = x1 + dx * t2 + offset2;
                const py2 = y1 + dy * t2;

                ctx.drawLine(px1, py1, px2, py2);
            }

            ctx.setGlow(null, 0);
        }

        function drawMass(ctx, x, y, mass, time) {
            const size = 30 + mass * 10;

            // Shadow
            ctx.setFillStyle('#000000');
            ctx.setOpacity(0.3);
            ctx.drawRect(x - size / 2 + 5, y - size / 2 + 5, size, size);
            ctx.setOpacity(1.0);

            // Main mass body
            ctx.setFillStyle(COLORS.accent);
            ctx.setGlow(COLORS.accent, 20);
            ctx.drawRect(x - size / 2, y - size / 2, size, size);
            ctx.setGlow(null, 0);

            // Border
            ctx.setStrokeStyle(COLORS.text);
            ctx.setLineWidth(2);
            ctx.drawLine(x - size / 2, y - size / 2, x + size / 2, y - size / 2);
            ctx.drawLine(x + size / 2, y - size / 2, x + size / 2, y + size / 2);
            ctx.drawLine(x + size / 2, y + size / 2, x - size / 2, y + size / 2);
            ctx.drawLine(x - size / 2, y + size / 2, x - size / 2, y - size / 2);

            // Mass label
            ctx.setFillStyle(COLORS.text);
            ctx.setFontSize(18);
            ctx.drawText(`m`, x - 8, y + 5);

            // Pulsing effect
            const pulse = Math.sin(time * 3) * 0.5 + 0.5;
            ctx.setFillStyle(COLORS.primary);
            ctx.setOpacity(pulse * 0.3);
            ctx.drawRect(x - size / 2, y - size / 2, size, size);
            ctx.setOpacity(1.0);
        }

        function drawEquilibriumLine(ctx, y) {
            ctx.setStrokeStyle(COLORS.success);
            ctx.setOpacity(0.4);
            ctx.setLineWidth(2);
            ctx.setLineDash([10, 10]);
            ctx.drawLine(width * 0.15, y, width * 0.6, y);
            ctx.setLineDash([]);
            ctx.setOpacity(1.0);

            // Label
            ctx.setFillStyle(COLORS.success);
            ctx.setFontSize(14);
            ctx.drawText('平衡位置', width * 0.15 - 70, y - 5);
        }

        function drawVelocityVector(ctx, x, y, velocity) {
            const scale = 2;
            const vy = velocity * scale;
            const arrowSize = 12;

            // Calculate opacity based on velocity magnitude for smooth fade
            const minVisibleVelocity = 0.01;
            const fadeRange = 5;
            const opacity = Math.min(1, Math.abs(velocity) / fadeRange);

            if (Math.abs(velocity) < minVisibleVelocity) return;

            // Vector line
            ctx.setStrokeStyle(COLORS.success);
            ctx.setLineWidth(3);
            ctx.setOpacity(opacity * 0.8);
            ctx.setGlow(COLORS.success, 10);
            ctx.drawLine(x + 60, y, x + 60, y + vy);
            ctx.setGlow(null, 0);

            // Arrowhead
            ctx.setFillStyle(COLORS.success);
            const tipY = y + vy;
            const dir = velocity > 0 ? 1 : -1;

            ctx.drawPath([
                { x: x + 60, y: tipY },
                { x: x + 60 - arrowSize / 2, y: tipY - arrowSize * dir },
                { x: x + 60 + arrowSize / 2, y: tipY - arrowSize * dir }
            ], true);

            // Label
            ctx.setFillStyle(COLORS.success);
            ctx.setFontSize(16);
            ctx.drawText('v', x + 75, y + vy / 2);
            ctx.setOpacity(1.0);
        }

        function drawForceVector(ctx, x, y, force, color, label) {
            const scale = 5;
            const fy = force * scale;
            const arrowSize = 12;

            // Calculate opacity based on force magnitude for smooth fade
            const minVisibleForce = 0.01;
            const fadeRange = 3;
            const opacity = Math.min(1, Math.abs(force) / fadeRange);

            if (Math.abs(force) < minVisibleForce) return;

            // Vector line
            ctx.setStrokeStyle(color);
            ctx.setLineWidth(3);
            ctx.setOpacity(opacity * 0.8);
            ctx.setGlow(color, 10);
            ctx.drawLine(x - 60, y, x - 60, y + fy);
            ctx.setGlow(null, 0);

            // Arrowhead
            ctx.setFillStyle(color);
            const tipY = y + fy;
            const dir = force > 0 ? 1 : -1;

            ctx.drawPath([
                { x: x - 60, y: tipY },
                { x: x - 60 - arrowSize / 2, y: tipY - arrowSize * dir },
                { x: x - 60 + arrowSize / 2, y: tipY - arrowSize * dir }
            ], true);

            // Label
            ctx.setFillStyle(color);
            ctx.setFontSize(16);
            ctx.drawText(label, x - 85, y + fy / 2);
            ctx.setOpacity(1.0);
        }

        function drawEnergyGraph(ctx, history, x, y, w, h) {
            if (history.length < 2) return;

            // Panel background
            ctx.setFillStyle(COLORS.background);
            ctx.setOpacity(0.9);
            ctx.drawRect(x, y, w, h);
            ctx.setOpacity(1.0);

            // Border
            ctx.setStrokeStyle(COLORS.primary);
            ctx.setLineWidth(2);
            ctx.setGlow(COLORS.primary, 8);
            ctx.drawLine(x, y, x + w, y);
            ctx.drawLine(x + w, y, x + w, y + h);
            ctx.drawLine(x + w, y + h, x, y + h);
            ctx.drawLine(x, y + h, x, y);
            ctx.setGlow(null, 0);

            // Title
            ctx.setFillStyle(COLORS.text);
            ctx.setFontSize(16);
            ctx.drawText('能量-时间图', x + 10, y + 20);

            // Find max energy for scaling
            const maxEnergy = Math.max(...history.map(h => h.total), 1);

            // Draw kinetic energy
            drawEnergyLine(ctx, history, x, y + h - 10, w, h - 40, maxEnergy, 'kinetic', COLORS.success);

            // Draw potential energy
            drawEnergyLine(ctx, history, x, y + h - 10, w, h - 40, maxEnergy, 'potential', COLORS.danger);

            // Draw total energy
            drawEnergyLine(ctx, history, x, y + h - 10, w, h - 40, maxEnergy, 'total', COLORS.primary);

            // Legend
            drawLegend(ctx, x + 10, y + h - 25, [
                { color: COLORS.success, label: '动能' },
                { color: COLORS.danger, label: '势能' },
                { color: COLORS.primary, label: '总能量' }
            ]);
        }

        function drawEnergyLine(ctx, history, x, y, w, h, maxEnergy, key, color) {
            ctx.setStrokeStyle(color);
            ctx.setLineWidth(2);
            ctx.setOpacity(0.8);

            for (let i = 0; i < history.length - 1; i++) {
                const x1 = x + (i / history.length) * w;
                const x2 = x + ((i + 1) / history.length) * w;
                const y1 = y - (history[i][key] / maxEnergy) * h;
                const y2 = y - (history[i + 1][key] / maxEnergy) * h;

                ctx.drawLine(x1, y1, x2, y2);
            }

            ctx.setOpacity(1.0);
        }

        function drawEnergyBars(ctx, kinetic, potential, total, maxEnergyScale, x, y, w, h) {
            // Panel background
            ctx.setFillStyle(COLORS.background);
            ctx.setOpacity(0.9);
            ctx.drawRect(x, y, w, h);
            ctx.setOpacity(1.0);

            // Border
            ctx.setStrokeStyle(COLORS.secondary);
            ctx.setLineWidth(2);
            ctx.drawLine(x, y, x + w, y);
            ctx.drawLine(x + w, y, x + w, y + h);
            ctx.drawLine(x + w, y + h, x, y + h);
            ctx.drawLine(x, y + h, x, y);

            // Title
            ctx.setFillStyle(COLORS.text);
            ctx.setFontSize(16);
            ctx.drawText('能量分布', x + 10, y + 20);

            const barWidth = w * 0.25;
            const maxBarHeight = h * 0.6;
            const maxEnergy = Math.max(maxEnergyScale, 1);

            // Kinetic energy bar
            const kHeight = (kinetic / maxEnergy) * maxBarHeight;
            ctx.setFillStyle(COLORS.success);
            ctx.setGlow(COLORS.success, 10);
            ctx.drawRect(x + 20, y + h - 30 - kHeight, barWidth, kHeight);
            ctx.setGlow(null, 0);
            ctx.setFillStyle(COLORS.text);
            ctx.setFontSize(12);
            ctx.drawText('Ek', x + 20 + barWidth / 2 - 10, y + h - 10);

            // Potential energy bar
            const pHeight = (potential / maxEnergy) * maxBarHeight;
            ctx.setFillStyle(COLORS.danger);
            ctx.setGlow(COLORS.danger, 10);
            ctx.drawRect(x + 60 + barWidth, y + h - 30 - pHeight, barWidth, pHeight);
            ctx.setGlow(null, 0);
            ctx.setFillStyle(COLORS.text);
            ctx.setFontSize(12);
            ctx.drawText('Ep', x + 60 + barWidth + barWidth / 2 - 10, y + h - 10);
        }

        function drawLegend(ctx, x, y, items) {
            const spacing = 70;
            items.forEach((item, i) => {
                ctx.setFillStyle(item.color);
                ctx.drawRect(x + i * spacing, y, 15, 3);
                ctx.setFillStyle(COLORS.text);
                ctx.setFontSize(11);
                ctx.drawText(item.label, x + i * spacing + 20, y + 5);
            });
        }

        function drawInfoPanel(ctx, x, y, lines) {
            const padding = 15;
            const lineHeight = 25;
            const panelWidth = width * 0.22;
            const panelHeight = lines.length * lineHeight + padding * 2;

            // Panel background
            ctx.setFillStyle(COLORS.background);
            ctx.setOpacity(0.85);
            ctx.drawRect(x, y, panelWidth, panelHeight);
            ctx.setOpacity(1.0);

            // Border
            ctx.setStrokeStyle(COLORS.primary);
            ctx.setLineWidth(2);
            ctx.setGlow(COLORS.primary, 8);
            ctx.drawLine(x, y, x + panelWidth, y);
            ctx.drawLine(x + panelWidth, y, x + panelWidth, y + panelHeight);
            ctx.drawLine(x + panelWidth, y + panelHeight, x, y + panelHeight);
            ctx.drawLine(x, y + panelHeight, x, y);
            ctx.setGlow(null, 0);

            // Text
            ctx.setFillStyle(COLORS.text);
            ctx.setFontSize(15);
            lines.forEach((line, i) => {
                ctx.drawText(line, x + padding, y + padding + (i + 1) * lineHeight);
            });
        }

        function drawParametersPanel(ctx, x, y, lines) {
            const padding = 15;
            const lineHeight = 25;
            const panelWidth = width * 0.22;
            const panelHeight = lines.length * lineHeight + padding * 2;

            // Panel background
            ctx.setFillStyle(COLORS.background);
            ctx.setOpacity(0.85);
            ctx.drawRect(x, y, panelWidth, panelHeight);
            ctx.setOpacity(1.0);

            // Border
            ctx.setStrokeStyle(COLORS.secondary);
            ctx.setLineWidth(2);
            ctx.drawLine(x, y, x + panelWidth, y);
            ctx.drawLine(x + panelWidth, y, x + panelWidth, y + panelHeight);
            ctx.drawLine(x + panelWidth, y + panelHeight, x, y + panelHeight);
            ctx.drawLine(x, y + panelHeight, x, y);

            // Text
            ctx.setFillStyle(COLORS.text);
            ctx.setFontSize(15);
            lines.forEach((line, i) => {
                ctx.drawText(line, x + padding, y + padding + (i + 1) * lineHeight);
            });
        }

        function drawControlPanel(ctx, x, y) {
            const padding = 15;
            const panelWidth = width * 0.22;
            const panelHeight = height * 0.15;

            // Panel background
            ctx.setFillStyle(COLORS.background);
            ctx.setOpacity(0.85);
            ctx.drawRect(x, y, panelWidth, panelHeight);
            ctx.setOpacity(1.0);

            // Border
            ctx.setStrokeStyle(COLORS.accent);
            ctx.setLineWidth(2);
            ctx.drawLine(x, y, x + panelWidth, y);
            ctx.drawLine(x + panelWidth, y, x + panelWidth, y + panelHeight);
            ctx.drawLine(x + panelWidth, y + panelHeight, x, y + panelHeight);
            ctx.drawLine(x, y + panelHeight, x, y);

            // Instructions
            ctx.setFillStyle(COLORS.text);
            ctx.setFontSize(14);
            ctx.drawText('控制说明:', x + padding, y + padding + 20);
            ctx.setFontSize(12);
            ctx.drawText('• 拖拽质点改变位置', x + padding, y + padding + 45);
            ctx.drawText('• 释放观察振动', x + padding, y + padding + 65);
            ctx.drawText('• 观察能量转换', x + padding, y + padding + 85);
        }

        function drawTitle(ctx, x, y, text) {
            ctx.setFillStyle(COLORS.text);
            ctx.setFontSize(32);
            ctx.setGlow(COLORS.accent, 15);
            ctx.drawText(text, x - text.length * 8, y);
            ctx.setGlow(null, 0);
        }

        function drawDecorativeParticles(ctx, x, y, time, velocity) {
            const particleCount = 8;
            for (let i = 0; i < particleCount; i++) {
                const angle = (i / particleCount) * Math.PI * 2 + time;
                const radius = 60 + Math.abs(velocity) * 0.5;
                const px = x + Math.cos(angle) * radius;
                const py = y + Math.sin(angle) * radius;
                const size = 3 + Math.sin(time * 2 + i) * 1.5;

                ctx.setFillStyle(COLORS.accent);
                ctx.setOpacity(0.4);
                ctx.drawCircle(px, py, size);
            }
            ctx.setOpacity(1.0);
        }

        function drawDisplacementIndicator(ctx, x1, y1, x2, y2) {
            const displacement = Math.abs(y2 - y1);

            // Calculate opacity based on displacement for smooth fade
            const minVisibleDisplacement = 2;
            const fadeRange = 20;
            const opacity = Math.min(1, Math.max(0, (displacement - minVisibleDisplacement) / fadeRange));

            if (displacement < minVisibleDisplacement) return;

            // Double arrow
            ctx.setStrokeStyle(COLORS.secondary);
            ctx.setLineWidth(2);
            ctx.setOpacity(opacity * 0.7);
            ctx.drawLine(x1, y1, x2, y2);

            // Arrowheads
            ctx.setFillStyle(COLORS.secondary);
            const arrowSize = 8;

            // Top arrow
            ctx.drawPath([
                { x: x1, y: y1 },
                { x: x1 - arrowSize / 2, y: y1 + arrowSize },
                { x: x1 + arrowSize / 2, y: y1 + arrowSize }
            ], true);

            // Bottom arrow
            ctx.drawPath([
                { x: x2, y: y2 },
                { x: x2 - arrowSize / 2, y: y2 - arrowSize },
                { x: x2 + arrowSize / 2, y: y2 - arrowSize }
            ], true);

            // Label
            ctx.setFillStyle(COLORS.secondary);
            ctx.setFontSize(14);
            ctx.drawText('Δx', x1 - 25, (y1 + y2) / 2);
            ctx.setOpacity(1.0);
        }

        // Mock context implementation
        function createMockContext(canvas) {
            const realCtx = canvas.getContext('2d');

            const ctx = {
                setFillStyle(color) { realCtx.fillStyle = color; },
                setStrokeStyle(color) { realCtx.strokeStyle = color; },
                setLineWidth(width) { realCtx.lineWidth = width; },
                setOpacity(alpha) { realCtx.globalAlpha = alpha; },
                setFontSize(size) { realCtx.font = `${size}px 'Segoe UI', sans-serif`; },
                setLineDash(segments) { realCtx.setLineDash(segments); },
                setGlow(color, blur) {
                    if (color) {
                        realCtx.shadowColor = color;
                        realCtx.shadowBlur = blur;
                    } else {
                        realCtx.shadowColor = 'transparent';
                        realCtx.shadowBlur = 0;
                    }
                },
                drawRect(x, y, w, h) {
                    realCtx.fillRect(x, y, w, h);
                },
                drawCircle(x, y, radius) {
                    realCtx.beginPath();
                    realCtx.arc(x, y, radius, 0, Math.PI * 2);
                    realCtx.fill();
                },
                drawLine(x1, y1, x2, y2) {
                    realCtx.beginPath();
                    realCtx.moveTo(x1, y1);
                    realCtx.lineTo(x2, y2);
                    realCtx.stroke();
                },
                drawText(text, x, y) {
                    realCtx.fillText(text, x, y);
                },
                drawPath(points, close = false) {
                    if (points.length === 0) return;
                    realCtx.beginPath();
                    realCtx.moveTo(points[0].x, points[0].y);
                    for (let i = 1; i < points.length; i++) {
                        realCtx.lineTo(points[i].x, points[i].y);
                    }
                    if (close) realCtx.closePath();
                    realCtx.fill();
                },
                onDrag(callback) {
                    let dragging = false;
                    canvas.addEventListener('mousedown', (e) => {
                        dragging = true;
                        const rect = canvas.getBoundingClientRect();
                        callback(e.clientX - rect.left, e.clientY - rect.top, 'start');
                    });
                    canvas.addEventListener('mousemove', (e) => {
                        if (dragging) {
                            const rect = canvas.getBoundingClientRect();
                            callback(e.clientX - rect.left, e.clientY - rect.top, 'move');
                        }
                    });
                    canvas.addEventListener('mouseup', () => {
                        if (dragging) {
                            dragging = false;
                            callback(0, 0, 'end');
                        }
                    });
                }
            };

            return ctx;
        }

        // Initialize
        const ctx = createMockContext(canvas);
        const state = setup(ctx);
        const vars = { speed: 1.0 };
        let startTime = Date.now();

        // Setup drag interaction
        ctx.onDrag((x, y, phase) => {
            if (phase === 'start') {
                const dx = x - state.fixedPointX;
                const dy = y - (state.equilibriumY + state.displacement);
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 50) {
                    state.isDragging = true;
                }
            } else if (phase === 'move' && state.isDragging) {
                const newDisplacement = y - state.equilibriumY;
                // Smooth the dragging motion
                state.displacement = state.displacement * 0.7 + newDisplacement * 0.3;
                state.velocity = 0;
            } else if (phase === 'end') {
                state.isDragging = false;
                // Reset oscillation count when releasing
                state.oscillationCount = 0;
                state.lastDisplacement = state.displacement;
            }
        });

        // Animation loop
        function animate() {
            const time = Date.now() - startTime;
            update(ctx, state, time, vars);
            requestAnimationFrame(animate);
        }

        animate();
    </script>
</body>
</html>$HTML$,
 75,
 197,
 784,
 false,
 0,
 NOW(),
 '{"name": "弹簧振子", "description": "弹簧振子的简谐运动，展示弹性势能和动能的转换", "difficulty": "medium", "render_mode": "html"}');


-- [4/24] 细胞分裂 (biology, 75分)
INSERT INTO simulator_templates
(subject, topic, code, quality_score, visual_elements, line_count, has_setup_update, variable_count, created_at, metadata)
VALUES
('biology',
 '细胞分裂',
 $HTML$<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>细胞有丝分裂模拟器</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
            color: #F1F5F9;
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        h1 {
            text-align: center;
            color: #22C55E;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 0 0 20px rgba(34, 197, 94, 0.5);
        }
        .main-content {
            display: grid;
            grid-template-columns: 1fr 400px;
            gap: 20px;
            margin-bottom: 20px;
        }
        .canvas-section {
            background: rgba(15, 23, 42, 0.8);
            border-radius: 15px;
            padding: 20px;
            border: 2px solid #22C55E;
            box-shadow: 0 0 30px rgba(34, 197, 94, 0.3);
        }
        canvas {
            display: block;
            width: 100%;
            height: 600px;
            background: #0F172A;
            border-radius: 10px;
            cursor: crosshair;
        }
        .control-panel {
            background: rgba(15, 23, 42, 0.8);
            border-radius: 15px;
            padding: 20px;
            border: 2px solid #EC4899;
            box-shadow: 0 0 30px rgba(236, 72, 153, 0.3);
        }
        .control-group {
            margin-bottom: 20px;
        }
        .control-group h3 {
            color: #EC4899;
            margin-bottom: 10px;
            font-size: 1.2em;
        }
        .phase-buttons {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 15px;
        }
        button {
            background: linear-gradient(135deg, #22C55E 0%, #16A34A 100%);
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            font-weight: bold;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(34, 197, 94, 0.3);
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(34, 197, 94, 0.5);
        }
        button.active {
            background: linear-gradient(135deg, #EC4899 0%, #DB2777 100%);
            box-shadow: 0 4px 15px rgba(236, 72, 153, 0.3);
        }
        .slider-group {
            margin-bottom: 15px;
        }
        .slider-group label {
            display: block;
            margin-bottom: 5px;
            color: #F59E0B;
            font-weight: bold;
        }
        input[type="range"] {
            width: 100%;
            height: 6px;
            border-radius: 3px;
            background: #334155;
            outline: none;
            -webkit-appearance: none;
        }
        input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #22C55E;
            cursor: pointer;
            box-shadow: 0 0 10px rgba(34, 197, 94, 0.5);
        }
        .stats {
            background: rgba(30, 41, 59, 0.6);
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
        }
        .stat-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            padding: 8px;
            background: rgba(15, 23, 42, 0.5);
            border-radius: 5px;
        }
        .stat-label {
            color: #94A3B8;
        }
        .stat-value {
            color: #22C55E;
            font-weight: bold;
        }
        .info-panel {
            background: rgba(15, 23, 42, 0.8);
            border-radius: 15px;
            padding: 20px;
            border: 2px solid #F59E0B;
            box-shadow: 0 0 30px rgba(245, 158, 11, 0.3);
        }
        .info-panel h3 {
            color: #F59E0B;
            margin-bottom: 15px;
        }
        .phase-info {
            background: rgba(30, 41, 59, 0.6);
            padding: 15px;
            border-radius: 8px;
            line-height: 1.6;
        }
        .legend {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-top: 15px;
        }
        .legend-item {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .legend-color {
            width: 30px;
            height: 30px;
            border-radius: 5px;
            border: 2px solid rgba(255, 255, 255, 0.3);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧬 细胞有丝分裂模拟器</h1>

        <div class="main-content">
            <div class="canvas-section">
                <canvas id="simulationCanvas"></canvas>
            </div>

            <div class="control-panel">
                <div class="control-group">
                    <h3>分裂时期</h3>
                    <div class="phase-buttons">
                        <button onclick="setPhase('interphase')" id="btn-interphase">间期</button>
                        <button onclick="setPhase('prophase')" id="btn-prophase">前期</button>
                        <button onclick="setPhase('prometaphase')" id="btn-prometaphase">前中期</button>
                        <button onclick="setPhase('metaphase')" id="btn-metaphase">中期</button>
                        <button onclick="setPhase('anaphase')" id="btn-anaphase">后期</button>
                        <button onclick="setPhase('telophase')" id="btn-telophase">末期</button>
                    </div>
                </div>

                <div class="control-group">
                    <div class="slider-group">
                        <label>动画速度: <span id="speedValue">1.0</span>x</label>
                        <input type="range" id="speedSlider" min="0.1" max="3" step="0.1" value="1">
                    </div>
                    <div class="slider-group">
                        <label>染色体数量: <span id="chromoValue">4</span></label>
                        <input type="range" id="chromoSlider" min="2" max="8" step="2" value="4">
                    </div>
                </div>

                <div class="control-group">
                    <button onclick="toggleAnimation()" id="playBtn" style="width: 100%; margin-bottom: 10px;">▶ 播放动画</button>
                    <button onclick="resetSimulation()" style="width: 100%; background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);">🔄 重置</button>
                </div>

                <div class="stats">
                    <div class="stat-item">
                        <span class="stat-label">当前时期</span>
                        <span class="stat-value" id="currentPhase">间期</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">染色体数量</span>
                        <span class="stat-value" id="chromoCount">4</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">染色单体数量</span>
                        <span class="stat-value" id="chromatidCount">0</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">DNA含量</span>
                        <span class="stat-value" id="dnaContent">2C</span>
                    </div>
                </div>
            </div>
        </div>

        <div class="info-panel">
            <h3>时期说明</h3>
            <div class="phase-info" id="phaseDescription">
                <strong>间期（Interphase）</strong><br>
                细胞生长，DNA复制（S期），形成染色单体。核膜完整，染色质呈丝状分散。此期DNA含量从2C增至4C。
            </div>

            <div class="legend">
                <div class="legend-item">
                    <div class="legend-color" style="background: #EC4899;"></div>
                    <span>染色体/染色质</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #22C55E;"></div>
                    <span>纺锤体微管</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #60A5FA;"></div>
                    <span>核膜</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #F59E0B;"></div>
                    <span>着丝点</span>
                </div>
            </div>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('simulationCanvas');
        const ctx = canvas.getContext('2d');

        // 设置实际画布尺寸
        canvas.width = canvas.offsetWidth;
        canvas.height = canvas.offsetHeight;

        const COLORS = {
            primary: '#22C55E',
            secondary: '#EC4899',
            accent: '#F59E0B',
            background: '#1E293B',
            text: '#F1F5F9',
            nuclear: '#60A5FA'
        };

        let currentPhase = 'interphase';
        let animationSpeed = 1.0;
        let chromosomeCount = 4;
        let isAnimating = false;
        let animationFrame = 0;
        let animationId = null;

        const phaseDescriptions = {
            interphase: {
                title: '间期（Interphase）',
                desc: '细胞生长，DNA复制（S期），形成染色单体。核膜完整，染色质呈丝状分散。此期DNA含量从2C增至4C。',
                dna: '4C',
                chromatids: 0
            },
            prophase: {
                title: '前期（Prophase）',
                desc: '染色质高度螺旋化凝缩成染色体，每条染色体含两条姐妹染色单体。中心体移向两极，开始形成纺锤体。核膜核仁逐渐消失。',
                dna: '4C',
                chromatids: chromosomeCount * 2
            },
            prometaphase: {
                title: '前中期（Prometaphase）',
                desc: '核膜完全消失，纺锤体充分形成。染色体散乱分布，纺锤丝附着到着丝点。染色体开始向赤道板移动。',
                dna: '4C',
                chromatids: chromosomeCount * 2
            },
            metaphase: {
                title: '中期（Metaphase）',
                desc: '所有染色体的着丝点排列在细胞赤道板上，形成整齐的中期板。纺锤丝连接着丝点，染色体形态最清晰，是观察染色体的最佳时期。',
                dna: '4C',
                chromatids: chromosomeCount * 2
            },
            anaphase: {
                title: '后期（Anaphase）',
                desc: '着丝点分裂，姐妹染色单体分开成为独立的染色体，在纺锤丝牵引下移向两极。细胞两极的染色体数目相等，均为体细胞染色体数。',
                dna: '4C→2C',
                chromatids: 0
            },
            telophase: {
                title: '末期（Telophase）',
                desc: '染色体解螺旋成染色质，纺锤体消失。核膜、核仁重新出现。细胞中部出现细胞板（植物）或缢裂（动物），最终分裂成两个子细胞。',
                dna: '2C',
                chromatids: 0
            }
        };

        class Chromosome {
            constructor(x, y, angle, color) {
                this.x = x;
                this.y = y;
                this.targetX = x;
                this.targetY = y;
                this.angle = angle;
                this.color = color;
                this.size = 30;
                this.separated = false;
                this.partner = null;
            }

            draw(phase) {
                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.angle);

                if (phase === 'interphase') {
                    // 间期：松散的染色质
                    ctx.strokeStyle = this.color;
                    ctx.lineWidth = 2;
                    ctx.globalAlpha = 0.5;
                    for (let i = 0; i < 5; i++) {
                        ctx.beginPath();
                        ctx.moveTo(-20 + i * 10, -20);
                        ctx.quadraticCurveTo(-10 + i * 10, 0, -20 + i * 10, 20);
                        ctx.stroke();
                    }
                } else if (phase === 'prophase' || phase === 'prometaphase' || phase === 'metaphase') {
                    // 前期到中期：X形染色体（两条姐妹染色单体）
                    ctx.fillStyle = this.color;

                    // 左侧染色单体
                    ctx.beginPath();
                    ctx.ellipse(-8, -15, 5, 18, 0, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.beginPath();
                    ctx.ellipse(-8, 15, 5, 18, 0, 0, Math.PI * 2);
                    ctx.fill();

                    // 右侧染色单体
                    ctx.beginPath();
                    ctx.ellipse(8, -15, 5, 18, 0, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.beginPath();
                    ctx.ellipse(8, 15, 5, 18, 0, 0, Math.PI * 2);
                    ctx.fill();

                    // 着丝点
                    ctx.fillStyle = COLORS.accent;
                    ctx.beginPath();
                    ctx.arc(0, 0, 6, 0, Math.PI * 2);
                    ctx.fill();
                } else {
                    // 后期和末期：单条染色体
                    ctx.fillStyle = this.color;
                    ctx.beginPath();
                    ctx.ellipse(0, -12, 5, 15, 0, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.beginPath();
                    ctx.ellipse(0, 12, 5, 15, 0, 0, Math.PI * 2);
                    ctx.fill();

                    // 着丝点
                    ctx.fillStyle = COLORS.accent;
                    ctx.beginPath();
                    ctx.arc(0, 0, 4, 0, Math.PI * 2);
                    ctx.fill();
                }

                ctx.restore();
            }

            update() {
                this.x += (this.targetX - this.x) * 0.05;
                this.y += (this.targetY - this.y) * 0.05;
            }
        }

        let chromosomes = [];

        function initChromosomes() {
            chromosomes = [];
            const centerX = canvas.width / 2;
            const centerY = canvas.height / 2;

            for (let i = 0; i < chromosomeCount; i++) {
                const angle = (Math.PI * 2 / chromosomeCount) * i;
                const radius = 60;
                const x = centerX + Math.cos(angle) * radius;
                const y = centerY + Math.sin(angle) * radius;
                const color = `hsl(${(i / chromosomeCount) * 360}, 70%, 60%)`;

                const chromo = new Chromosome(x, y, angle, color);
                chromosomes.push(chromo);
            }
        }

        function drawNuclearMembrane(alpha = 1) {
            const centerX = canvas.width / 2;
            const centerY = canvas.height / 2;
            const radius = 150;

            ctx.strokeStyle = COLORS.nuclear;
            ctx.lineWidth = 3;
            ctx.globalAlpha = alpha;
            ctx.beginPath();
            ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
            ctx.stroke();
            ctx.globalAlpha = 1;
        }

        function drawSpindle(alpha = 1) {
            const centerX = canvas.width / 2;
            const centerY = canvas.height / 2;
            const poleDistance = 250;

            ctx.strokeStyle = COLORS.primary;
            ctx.lineWidth = 2;
            ctx.globalAlpha = alpha * 0.6;

            // 左极到右极
            const leftPoleX = centerX - poleDistance;
            const rightPoleX = centerX + poleDistance;

            // 绘制纺锤丝
            for (let i = 0; i < 12; i++) {
                const offset = (i - 6) * 15;
                ctx.beginPath();
                ctx.moveTo(leftPoleX, centerY);
                ctx.quadraticCurveTo(centerX, centerY + offset, rightPoleX, centerY);
                ctx.stroke();
            }

            // 绘制中心体
            ctx.fillStyle = COLORS.primary;
            ctx.globalAlpha = alpha;
            ctx.beginPath();
            ctx.arc(leftPoleX, centerY, 8, 0, Math.PI * 2);
            ctx.fill();
            ctx.beginPath();
            ctx.arc(rightPoleX, centerY, 8, 0, Math.PI * 2);
            ctx.fill();

            ctx.globalAlpha = 1;
        }

        function updatePhasePositions() {
            const centerX = canvas.width / 2;
            const centerY = canvas.height / 2;

            switch(currentPhase) {
                case 'interphase':
                    chromosomes.forEach((chromo, i) => {
                        const angle = (Math.PI * 2 / chromosomeCount) * i + animationFrame * 0.001;
                        const radius = 80;
                        chromo.targetX = centerX + Math.cos(angle) * radius;
                        chromo.targetY = centerY + Math.sin(angle) * radius;
                        chromo.angle = angle;
                    });
                    break;

                case 'prophase':
                    chromosomes.forEach((chromo, i) => {
                        const angle = (Math.PI * 2 / chromosomeCount) * i;
                        const radius = 100;
                        chromo.targetX = centerX + Math.cos(angle) * radius;
                        chromo.targetY = centerY + Math.sin(angle) * radius;
                        chromo.angle = angle + Math.PI / 2;
                    });
                    break;

                case 'prometaphase':
                    chromosomes.forEach((chromo, i) => {
                        const angle = (Math.PI * 2 / chromosomeCount) * i + Math.sin(animationFrame * 0.02) * 0.3;
                        const radius = 70 + Math.sin(animationFrame * 0.03 + i) * 20;
                        chromo.targetX = centerX + Math.cos(angle) * radius;
                        chromo.targetY = centerY + Math.sin(angle) * radius;
                        chromo.angle = Math.PI / 2;
                    });
                    break;

                case 'metaphase':
                    chromosomes.forEach((chromo, i) => {
                        const spacing = 50;
                        const totalWidth = (chromosomeCount - 1) * spacing;
                        chromo.targetX = centerX - totalWidth / 2 + i * spacing;
                        chromo.targetY = centerY;
                        chromo.angle = Math.PI / 2;
                    });
                    break;

                case 'anaphase':
                    chromosomes.forEach((chromo, i) => {
                        const spacing = 50;
                        const totalWidth = (chromosomeCount - 1) * spacing;
                        const baseX = centerX - totalWidth / 2 + i * spacing;

                        if (i < chromosomeCount / 2) {
                            chromo.targetX = baseX - 120;
                        } else {
                            chromo.targetX = baseX + 120;
                        }
                        chromo.targetY = centerY;
                        chromo.angle = Math.PI / 2;
                    });
                    break;

                case 'telophase':
                    chromosomes.forEach((chromo, i) => {
                        const angle = (Math.PI * 2 / (chromosomeCount / 2)) * (i % (chromosomeCount / 2));
                        const radius = 50;

                        if (i < chromosomeCount / 2) {
                            chromo.targetX = centerX - 150 + Math.cos(angle) * radius;
                            chromo.targetY = centerY + Math.sin(angle) * radius;
                        } else {
                            chromo.targetX = centerX + 150 + Math.cos(angle) * radius;
                            chromo.targetY = centerY + Math.sin(angle) * radius;
                        }
                        chromo.angle = angle;
                    });
                    break;
            }
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // 绘制细胞膜
            ctx.strokeStyle = COLORS.text;
            ctx.lineWidth = 2;
            ctx.globalAlpha = 0.3;
            ctx.strokeRect(50, 50, canvas.width - 100, canvas.height - 100);
            ctx.globalAlpha = 1;

            // 根据时期绘制结构
            switch(currentPhase) {
                case 'interphase':
                    drawNuclearMembrane(1);
                    break;
                case 'prophase':
                    drawNuclearMembrane(0.5);
                    drawSpindle(0.3);
                    break;
                case 'prometaphase':
                    drawSpindle(0.7);
                    break;
                case 'metaphase':
                    drawSpindle(1);
                    break;
                case 'anaphase':
                    drawSpindle(0.8);
                    break;
                case 'telophase':
                    drawNuclearMembrane(0.6);
                    drawSpindle(0.2);

                    // 绘制两个核膜
                    ctx.strokeStyle = COLORS.nuclear;
                    ctx.lineWidth = 3;
                    ctx.globalAlpha = 0.8;
                    ctx.beginPath();
                    ctx.arc(canvas.width / 2 - 150, canvas.height / 2, 80, 0, Math.PI * 2);
                    ctx.stroke();
                    ctx.beginPath();
                    ctx.arc(canvas.width / 2 + 150, canvas.height / 2, 80, 0, Math.PI * 2);
                    ctx.stroke();
                    ctx.globalAlpha = 1;

                    // 绘制细胞板
                    ctx.strokeStyle = COLORS.accent;
                    ctx.lineWidth = 4;
                    ctx.beginPath();
                    ctx.moveTo(canvas.width / 2, 100);
                    ctx.lineTo(canvas.width / 2, canvas.height - 100);
                    ctx.stroke();
                    break;
            }

            // 绘制染色体
            chromosomes.forEach(chromo => {
                chromo.draw(currentPhase);
            });
        }

        function animate() {
            if (!isAnimating) return;

            animationFrame += animationSpeed;
            updatePhasePositions();
            chromosomes.forEach(chromo => chromo.update());
            draw();

            animationId = requestAnimationFrame(animate);
        }

        function setPhase(phase) {
            currentPhase = phase;
            animationFrame = 0;

            // 更新按钮状态
            document.querySelectorAll('.phase-buttons button').forEach(btn => {
                btn.classList.remove('active');
            });
            document.getElementById('btn-' + phase).classList.add('active');

            // 更新信息
            const info = phaseDescriptions[phase];
            document.getElementById('phaseDescription').innerHTML =
                `<strong>${info.title}</strong><br>${info.desc}`;
            document.getElementById('currentPhase').textContent = info.title.split('（')[0];
            document.getElementById('dnaContent').textContent = info.dna;
            document.getElementById('chromatidCount').textContent = info.chromatids;

            draw();
        }

        function toggleAnimation() {
            isAnimating = !isAnimating;
            const btn = document.getElementById('playBtn');

            if (isAnimating) {
                btn.textContent = '⏸ 暂停动画';
                animate();
            } else {
                btn.textContent = '▶ 播放动画';
                if (animationId) {
                    cancelAnimationFrame(animationId);
                }
            }
        }

        function resetSimulation() {
            isAnimating = false;
            if (animationId) {
                cancelAnimationFrame(animationId);
            }
            document.getElementById('playBtn').textContent = '▶ 播放动画';
            animationFrame = 0;
            initChromosomes();
            setPhase('interphase');
        }

        // 事件监听器
        document.getElementById('speedSlider').addEventListener('input', (e) => {
            animationSpeed = parseFloat(e.target.value);
            document.getElementById('speedValue').textContent = animationSpeed.toFixed(1);
        });

        document.getElementById('chromoSlider').addEventListener('input', (e) => {
            chromosomeCount = parseInt(e.target.value);
            document.getElementById('chromoValue').textContent = chromosomeCount;
            document.getElementById('chromoCount').textContent = chromosomeCount;
            initChromosomes();
            setPhase(currentPhase);
        });

        // 初始化
        initChromosomes();
        setPhase('interphase');
        draw();

        // 响应式调整
        window.addEventListener('resize', () => {
            canvas.width = canvas.offsetWidth;
            canvas.height = canvas.offsetHeight;
            initChromosomes();
            draw();
        });
    </script>
</body>
</html>
$HTML$,
 75,
 84,
 700,
 false,
 0,
 NOW(),
 '{"name": "细胞分裂", "description": "细胞有丝分裂过程的动态展示", "difficulty": "medium", "render_mode": "html"}');


-- [5/24] DNA复制 (biology, 75分)
INSERT INTO simulator_templates
(subject, topic, code, quality_score, visual_elements, line_count, has_setup_update, variable_count, created_at, metadata)
VALUES
('biology',
 'DNA复制',
 $HTML$<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DNA半保留复制模拟器</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
            color: #F1F5F9;
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        h1 {
            text-align: center;
            color: #22C55E;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 0 0 20px rgba(34, 197, 94, 0.5);
        }
        .main-content {
            display: grid;
            grid-template-columns: 1fr 400px;
            gap: 20px;
            margin-bottom: 20px;
        }
        .canvas-section {
            background: rgba(15, 23, 42, 0.8);
            border-radius: 15px;
            padding: 20px;
            border: 2px solid #22C55E;
            box-shadow: 0 0 30px rgba(34, 197, 94, 0.3);
        }
        canvas {
            display: block;
            width: 100%;
            height: 600px;
            background: #0F172A;
            border-radius: 10px;
            cursor: crosshair;
        }
        .control-panel {
            background: rgba(15, 23, 42, 0.8);
            border-radius: 15px;
            padding: 20px;
            border: 2px solid #EC4899;
            box-shadow: 0 0 30px rgba(236, 72, 153, 0.3);
        }
        .control-group {
            margin-bottom: 20px;
        }
        .control-group h3 {
            color: #EC4899;
            margin-bottom: 10px;
            font-size: 1.2em;
        }
        .step-buttons {
            display: grid;
            grid-template-columns: 1fr;
            gap: 10px;
            margin-bottom: 15px;
        }
        button {
            background: linear-gradient(135deg, #22C55E 0%, #16A34A 100%);
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            font-weight: bold;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(34, 197, 94, 0.3);
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(34, 197, 94, 0.5);
        }
        button.active {
            background: linear-gradient(135deg, #EC4899 0%, #DB2777 100%);
            box-shadow: 0 4px 15px rgba(236, 72, 153, 0.3);
        }
        .slider-group {
            margin-bottom: 15px;
        }
        .slider-group label {
            display: block;
            margin-bottom: 5px;
            color: #F59E0B;
            font-weight: bold;
        }
        input[type="range"] {
            width: 100%;
            height: 6px;
            border-radius: 3px;
            background: #334155;
            outline: none;
            -webkit-appearance: none;
        }
        input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #22C55E;
            cursor: pointer;
            box-shadow: 0 0 10px rgba(34, 197, 94, 0.5);
        }
        .stats {
            background: rgba(30, 41, 59, 0.6);
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
        }
        .stat-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            padding: 8px;
            background: rgba(15, 23, 42, 0.5);
            border-radius: 5px;
        }
        .stat-label {
            color: #94A3B8;
        }
        .stat-value {
            color: #22C55E;
            font-weight: bold;
        }
        .info-panel {
            background: rgba(15, 23, 42, 0.8);
            border-radius: 15px;
            padding: 20px;
            border: 2px solid #F59E0B;
            box-shadow: 0 0 30px rgba(245, 158, 11, 0.3);
        }
        .info-panel h3 {
            color: #F59E0B;
            margin-bottom: 15px;
        }
        .step-info {
            background: rgba(30, 41, 59, 0.6);
            padding: 15px;
            border-radius: 8px;
            line-height: 1.6;
        }
        .legend {
            display: grid;
            grid-template-columns: 1fr;
            gap: 10px;
            margin-top: 15px;
        }
        .legend-item {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .legend-color {
            width: 30px;
            height: 30px;
            border-radius: 5px;
            border: 2px solid rgba(255, 255, 255, 0.3);
        }
        .base-pair-info {
            background: rgba(30, 41, 59, 0.6);
            padding: 12px;
            border-radius: 8px;
            margin-top: 15px;
            text-align: center;
        }
        .base-pair-info h4 {
            color: #22C55E;
            margin-bottom: 8px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧬 DNA半保留复制模拟器</h1>

        <div class="main-content">
            <div class="canvas-section">
                <canvas id="simulationCanvas"></canvas>
            </div>

            <div class="control-panel">
                <div class="control-group">
                    <h3>复制步骤</h3>
                    <div class="step-buttons">
                        <button onclick="setStep('original')" id="btn-original">1. 原始双链DNA</button>
                        <button onclick="setStep('unwind')" id="btn-unwind">2. 解旋酶解旋</button>
                        <button onclick="setStep('binding')" id="btn-binding">3. 碱基配对</button>
                        <button onclick="setStep('completed')" id="btn-completed">4. 完成复制</button>
                    </div>
                </div>

                <div class="control-group">
                    <div class="slider-group">
                        <label>动画速度: <span id="speedValue">1.0</span>x</label>
                        <input type="range" id="speedSlider" min="0.1" max="3" step="0.1" value="1">
                    </div>
                    <div class="slider-group">
                        <label>碱基对数量: <span id="baseValue">12</span></label>
                        <input type="range" id="baseSlider" min="8" max="20" step="2" value="12">
                    </div>
                </div>

                <div class="control-group">
                    <button onclick="toggleAnimation()" id="playBtn" style="width: 100%; margin-bottom: 10px;">▶ 自动演示</button>
                    <button onclick="resetSimulation()" style="width: 100%; background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);">🔄 重置</button>
                </div>

                <div class="stats">
                    <div class="stat-item">
                        <span class="stat-label">当前步骤</span>
                        <span class="stat-value" id="currentStep">原始双链</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">碱基对数</span>
                        <span class="stat-value" id="basePairCount">12</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">解旋进度</span>
                        <span class="stat-value" id="unwindProgress">0%</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">新链合成</span>
                        <span class="stat-value" id="newStrand">0%</span>
                    </div>
                </div>

                <div class="base-pair-info">
                    <h4>碱基配对规则</h4>
                    <div style="color: #94A3B8; font-size: 0.9em;">
                        腺嘌呤(A) ⟷ 胸腺嘧啶(T)<br>
                        鸟嘌呤(G) ⟷ 胞嘧啶(C)
                    </div>
                </div>
            </div>
        </div>

        <div class="info-panel">
            <h3>步骤说明</h3>
            <div class="step-info" id="stepDescription">
                <strong>原始双链DNA</strong><br>
                DNA双螺旋结构，由两条反向平行的脱氧核苷酸链组成。通过氢键连接：A-T之间2个氢键，G-C之间3个氢键。
            </div>

            <div class="legend">
                <div class="legend-item">
                    <div class="legend-color" style="background: #3B82F6;"></div>
                    <span>腺嘌呤 (A) - 蓝色</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #EF4444;"></div>
                    <span>胸腺嘧啶 (T) - 红色</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #F59E0B;"></div>
                    <span>鸟嘌呤 (G) - 橙色</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #22C55E;"></div>
                    <span>胞嘧啶 (C) - 绿色</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #EC4899;"></div>
                    <span>母链 - 粉色骨架</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: #8B5CF6;"></div>
                    <span>新链 - 紫色骨架</span>
                </div>
            </div>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('simulationCanvas');
        const ctx = canvas.getContext('2d');

        canvas.width = canvas.offsetWidth;
        canvas.height = canvas.offsetHeight;

        const COLORS = {
            primary: '#22C55E',
            secondary: '#EC4899',
            accent: '#F59E0B',
            background: '#1E293B',
            text: '#F1F5F9',
            A: '#3B82F6',  // 腺嘌呤 - 蓝色
            T: '#EF4444',  // 胸腺嘧啶 - 红色
            G: '#F59E0B',  // 鸟嘌呤 - 橙色
            C: '#22C55E',  // 胞嘧啶 - 绿色
            oldStrand: '#EC4899',  // 母链
            newStrand: '#8B5CF6'   // 新链
        };

        let currentStep = 'original';
        let animationSpeed = 1.0;
        let basePairCount = 12;
        let isAnimating = false;
        let animationFrame = 0;
        let animationId = null;
        let unwindProgress = 0;
        let synthesisProgress = 0;

        const stepDescriptions = {
            original: {
                title: '原始双链DNA',
                desc: 'DNA双螺旋结构，由两条反向平行的脱氧核苷酸链组成。通过氢键连接：A-T之间2个氢键，G-C之间3个氢键。'
            },
            unwind: {
                title: '解旋酶解旋',
                desc: '解旋酶破坏氢键，使DNA双链分开形成复制叉。单链结合蛋白稳定单链DNA，防止重新结合。DNA聚合酶准备合成新链。'
            },
            binding: {
                title: '碱基配对',
                desc: 'DNA聚合酶沿母链移动，按照碱基互补配对原则（A-T, G-C）合成新链。每条母链作为模板合成一条新链。'
            },
            completed: {
                title: '完成复制',
                desc: '形成两个完全相同的DNA分子，每个包含一条母链和一条新链，这就是半保留复制。每个子代DNA保留了一半亲代DNA。'
            }
        };

        let sequence = [];

        function generateSequence() {
            const bases = ['A', 'T', 'G', 'C'];
            sequence = [];
            for (let i = 0; i < basePairCount; i++) {
                const base = bases[Math.floor(Math.random() * bases.length)];
                const complement = base === 'A' ? 'T' : base === 'T' ? 'A' : base === 'G' ? 'C' : 'G';
                sequence.push({ top: base, bottom: complement });
            }
        }

        class Base {
            constructor(type, x, y, strand) {
                this.type = type;
                this.x = x;
                this.y = y;
                this.targetX = x;
                this.targetY = y;
                this.strand = strand; // 'old' or 'new'
                this.alpha = 1;
            }

            draw() {
                ctx.save();
                ctx.globalAlpha = this.alpha;

                // 绘制碱基
                ctx.fillStyle = COLORS[this.type];
                ctx.beginPath();
                ctx.arc(this.x, this.y, 12, 0, Math.PI * 2);
                ctx.fill();

                // 绘制碱基字母
                ctx.fillStyle = '#FFF';
                ctx.font = 'bold 14px Arial';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(this.type, this.x, this.y);

                ctx.restore();
            }

            update() {
                this.x += (this.targetX - this.x) * 0.08;
                this.y += (this.targetY - this.y) * 0.08;
            }
        }

        let topBases = [];
        let bottomBases = [];
        let newTopBases = [];
        let newBottomBases = [];

        function initDNA() {
            generateSequence();
            topBases = [];
            bottomBases = [];
            newTopBases = [];
            newBottomBases = [];

            const startX = 100;
            const startY = canvas.height / 2;
            const spacing = (canvas.width - 200) / (basePairCount - 1);

            for (let i = 0; i < basePairCount; i++) {
                const x = startX + i * spacing;
                topBases.push(new Base(sequence[i].top, x, startY - 30, 'old'));
                bottomBases.push(new Base(sequence[i].bottom, x, startY + 30, 'old'));
            }
        }

        function drawBackbone(bases, color, offset = 0) {
            if (bases.length === 0) return;

            ctx.strokeStyle = color;
            ctx.lineWidth = 4;
            ctx.lineCap = 'round';
            ctx.lineJoin = 'round';

            ctx.beginPath();
            ctx.moveTo(bases[0].x, bases[0].y);

            for (let i = 1; i < bases.length; i++) {
                const prev = bases[i - 1];
                const curr = bases[i];
                const cp1x = prev.x + (curr.x - prev.x) / 3;
                const cp1y = prev.y + Math.sin(i * 0.5) * 10;
                const cp2x = prev.x + (curr.x - prev.x) * 2 / 3;
                const cp2y = curr.y + Math.sin(i * 0.5) * 10;

                ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, curr.x, curr.y);
            }

            ctx.stroke();
        }

        function drawHydrogenBonds() {
            ctx.strokeStyle = 'rgba(241, 245, 249, 0.3)';
            ctx.lineWidth = 2;
            ctx.setLineDash([5, 5]);

            for (let i = 0; i < Math.min(topBases.length, bottomBases.length); i++) {
                const top = topBases[i];
                const bottom = bottomBases[i];

                if (top && bottom && top.alpha > 0 && bottom.alpha > 0) {
                    const distance = Math.sqrt((top.x - bottom.x) ** 2 + (top.y - bottom.y) ** 2);
                    if (distance < 100) {
                        ctx.globalAlpha = Math.min(top.alpha, bottom.alpha);
                        ctx.beginPath();
                        ctx.moveTo(top.x, top.y);
                        ctx.lineTo(bottom.x, bottom.y);
                        ctx.stroke();
                    }
                }
            }

            ctx.globalAlpha = 1;
            ctx.setLineDash([]);
        }

        function updatePositions() {
            const centerY = canvas.height / 2;

            switch(currentStep) {
                case 'original':
                    unwindProgress = 0;
                    synthesisProgress = 0;
                    topBases.forEach((base, i) => {
                        base.targetY = centerY - 30;
                        base.alpha = 1;
                    });
                    bottomBases.forEach((base, i) => {
                        base.targetY = centerY + 30;
                        base.alpha = 1;
                    });
                    newTopBases = [];
                    newBottomBases = [];
                    break;

                case 'unwind':
                    unwindProgress = Math.min(100, unwindProgress + animationSpeed * 0.5);
                    const unwindIndex = Math.floor((unwindProgress / 100) * basePairCount);

                    topBases.forEach((base, i) => {
                        if (i < unwindIndex) {
                            base.targetY = centerY - 80;
                        } else {
                            base.targetY = centerY - 30;
                        }
                    });

                    bottomBases.forEach((base, i) => {
                        if (i < unwindIndex) {
                            base.targetY = centerY + 80;
                        } else {
                            base.targetY = centerY + 30;
                        }
                    });
                    break;

                case 'binding':
                    unwindProgress = 100;
                    synthesisProgress = Math.min(100, synthesisProgress + animationSpeed * 0.4);
                    const synthIndex = Math.floor((synthesisProgress / 100) * basePairCount);

                    topBases.forEach((base, i) => {
                        base.targetY = centerY - 80;
                    });

                    bottomBases.forEach((base, i) => {
                        base.targetY = centerY + 80;
                    });

                    // 创建新链碱基
                    const startX = 100;
                    const spacing = (canvas.width - 200) / (basePairCount - 1);

                    for (let i = 0; i < synthIndex; i++) {
                        const x = startX + i * spacing;

                        if (!newBottomBases[i]) {
                            newBottomBases[i] = new Base(sequence[i].top, x, centerY - 50, 'new');
                            newBottomBases[i].targetY = centerY - 50;
                            newBottomBases[i].alpha = 0;
                        }
                        newBottomBases[i].alpha = Math.min(1, newBottomBases[i].alpha + 0.05);

                        if (!newTopBases[i]) {
                            newTopBases[i] = new Base(sequence[i].bottom, x, centerY + 50, 'new');
                            newTopBases[i].targetY = centerY + 50;
                            newTopBases[i].alpha = 0;
                        }
                        newTopBases[i].alpha = Math.min(1, newTopBases[i].alpha + 0.05);
                    }
                    break;

                case 'completed':
                    unwindProgress = 100;
                    synthesisProgress = 100;

                    // 确保所有新链碱基都已创建
                    if (newTopBases.length < basePairCount) {
                        const startX = 100;
                        const spacing = (canvas.width - 200) / (basePairCount - 1);
                        for (let i = 0; i < basePairCount; i++) {
                            const x = startX + i * spacing;
                            if (!newBottomBases[i]) {
                                newBottomBases[i] = new Base(sequence[i].top, x, centerY - 50, 'new');
                            }
                            if (!newTopBases[i]) {
                                newTopBases[i] = new Base(sequence[i].bottom, x, centerY + 50, 'new');
                            }
                            newBottomBases[i].alpha = 1;
                            newTopBases[i].alpha = 1;
                        }
                    }

                    // 形成两个完整的DNA分子
                    const separation = 120;
                    topBases.forEach((base, i) => {
                        base.targetY = centerY - 30 - separation;
                    });
                    newBottomBases.forEach((base, i) => {
                        if (base) {
                            base.targetY = centerY + 30 - separation;
                        }
                    });

                    bottomBases.forEach((base, i) => {
                        base.targetY = centerY - 30 + separation;
                    });
                    newTopBases.forEach((base, i) => {
                        if (base) {
                            base.targetY = centerY + 30 + separation;
                        }
                    });
                    break;
            }
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // 绘制背景网格
            ctx.strokeStyle = 'rgba(148, 163, 184, 0.1)';
            ctx.lineWidth = 1;
            for (let i = 0; i < canvas.width; i += 50) {
                ctx.beginPath();
                ctx.moveTo(i, 0);
                ctx.lineTo(i, canvas.height);
                ctx.stroke();
            }
            for (let i = 0; i < canvas.height; i += 50) {
                ctx.beginPath();
                ctx.moveTo(0, i);
                ctx.lineTo(canvas.width, i);
                ctx.stroke();
            }

            // 绘制氢键
            drawHydrogenBonds();

            // 绘制骨架和碱基
            drawBackbone(topBases, COLORS.oldStrand);
            drawBackbone(bottomBases, COLORS.oldStrand);

            if (newTopBases.length > 0) {
                drawBackbone(newTopBases.filter(b => b && b.alpha > 0.5), COLORS.newStrand);
            }
            if (newBottomBases.length > 0) {
                drawBackbone(newBottomBases.filter(b => b && b.alpha > 0.5), COLORS.newStrand);
            }

            topBases.forEach(base => base.draw());
            bottomBases.forEach(base => base.draw());
            newTopBases.forEach(base => base && base.draw());
            newBottomBases.forEach(base => base && base.draw());

            // 绘制标签
            if (currentStep === 'completed') {
                ctx.fillStyle = COLORS.primary;
                ctx.font = 'bold 16px Arial';
                ctx.textAlign = 'center';
                ctx.fillText('DNA分子1 (含1条母链+1条新链)', canvas.width / 2, 80);
                ctx.fillText('DNA分子2 (含1条母链+1条新链)', canvas.width / 2, canvas.height - 60);
            }
        }

        function animate() {
            if (!isAnimating) return;

            animationFrame++;
            updatePositions();

            topBases.forEach(base => base.update());
            bottomBases.forEach(base => base.update());
            newTopBases.forEach(base => base && base.update());
            newBottomBases.forEach(base => base && base.update());

            draw();

            // 更新统计信息
            document.getElementById('unwindProgress').textContent = Math.round(unwindProgress) + '%';
            document.getElementById('newStrand').textContent = Math.round(synthesisProgress) + '%';

            animationId = requestAnimationFrame(animate);
        }

        function setStep(step) {
            currentStep = step;

            // 更新按钮状态
            document.querySelectorAll('.step-buttons button').forEach(btn => {
                btn.classList.remove('active');
            });
            document.getElementById('btn-' + step).classList.add('active');

            // 更新信息
            const info = stepDescriptions[step];
            document.getElementById('stepDescription').innerHTML =
                `<strong>${info.title}</strong><br>${info.desc}`;
            document.getElementById('currentStep').textContent = info.title;

            // 重置进度
            if (step === 'original') {
                unwindProgress = 0;
                synthesisProgress = 0;
                newTopBases = [];
                newBottomBases = [];
            }

            draw();
        }

        function toggleAnimation() {
            isAnimating = !isAnimating;
            const btn = document.getElementById('playBtn');

            if (isAnimating) {
                btn.textContent = '⏸ 暂停演示';
                animate();
            } else {
                btn.textContent = '▶ 自动演示';
                if (animationId) {
                    cancelAnimationFrame(animationId);
                }
            }
        }

        function resetSimulation() {
            isAnimating = false;
            if (animationId) {
                cancelAnimationFrame(animationId);
            }
            document.getElementById('playBtn').textContent = '▶ 自动演示';
            animationFrame = 0;
            unwindProgress = 0;
            synthesisProgress = 0;
            initDNA();
            setStep('original');
        }

        // 事件监听器
        document.getElementById('speedSlider').addEventListener('input', (e) => {
            animationSpeed = parseFloat(e.target.value);
            document.getElementById('speedValue').textContent = animationSpeed.toFixed(1);
        });

        document.getElementById('baseSlider').addEventListener('input', (e) => {
            basePairCount = parseInt(e.target.value);
            document.getElementById('baseValue').textContent = basePairCount;
            document.getElementById('basePairCount').textContent = basePairCount;
            initDNA();
            setStep(currentStep);
        });

        // 初始化
        initDNA();
        setStep('original');
        draw();

        // 响应式调整
        window.addEventListener('resize', () => {
            canvas.width = canvas.offsetWidth;
            canvas.height = canvas.offsetHeight;
            initDNA();
            draw();
        });
    </script>
</body>
</html>
$HTML$,
 75,
 46,
 730,
 false,
 0,
 NOW(),
 '{"name": "DNA复制", "description": "DNA双螺旋结构的解旋和复制过程", "difficulty": "hard", "render_mode": "html"}');


-- [6/24] 酶活性与米氏方程 (biology, 75分)
INSERT INTO simulator_templates
(subject, topic, code, quality_score, visual_elements, line_count, has_setup_update, variable_count, created_at, metadata)
VALUES
('biology',
 '酶活性与米氏方程',
 $HTML$<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>酶活性与米氏方程模拟器</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
            color: #F1F5F9;
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        h1 {
            text-align: center;
            color: #22C55E;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 0 0 20px rgba(34, 197, 94, 0.5);
        }
        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        .canvas-section {
            background: rgba(15, 23, 42, 0.8);
            border-radius: 15px;
            padding: 20px;
            border: 2px solid #22C55E;
            box-shadow: 0 0 30px rgba(34, 197, 94, 0.3);
        }
        .canvas-section h3 {
            color: #EC4899;
            margin-bottom: 15px;
            text-align: center;
        }
        canvas {
            display: block;
            width: 100%;
            height: 350px;
            background: #0F172A;
            border-radius: 10px;
        }
        .control-panel {
            background: rgba(15, 23, 42, 0.8);
            border-radius: 15px;
            padding: 20px;
            border: 2px solid #EC4899;
            box-shadow: 0 0 30px rgba(236, 72, 153, 0.3);
        }
        .control-group {
            margin-bottom: 20px;
        }
        .control-group h3 {
            color: #EC4899;
            margin-bottom: 10px;
            font-size: 1.2em;
        }
        .slider-group {
            margin-bottom: 15px;
            padding: 12px;
            background: rgba(30, 41, 59, 0.5);
            border-radius: 8px;
        }
        .slider-group label {
            display: block;
            margin-bottom: 5px;
            color: #F59E0B;
            font-weight: bold;
        }
        input[type="range"] {
            width: 100%;
            height: 6px;
            border-radius: 3px;
            background: #334155;
            outline: none;
            -webkit-appearance: none;
        }
        input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #22C55E;
            cursor: pointer;
            box-shadow: 0 0 10px rgba(34, 197, 94, 0.5);
        }
        button {
            background: linear-gradient(135deg, #22C55E 0%, #16A34A 100%);
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            font-weight: bold;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(34, 197, 94, 0.3);
            width: 100%;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(34, 197, 94, 0.5);
        }
        .stats {
            background: rgba(30, 41, 59, 0.6);
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
        }
        .stat-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            padding: 8px;
            background: rgba(15, 23, 42, 0.5);
            border-radius: 5px;
        }
        .stat-label {
            color: #94A3B8;
        }
        .stat-value {
            color: #22C55E;
            font-weight: bold;
        }
        .info-panel {
            background: rgba(15, 23, 42, 0.8);
            border-radius: 15px;
            padding: 20px;
            border: 2px solid #F59E0B;
            box-shadow: 0 0 30px rgba(245, 158, 11, 0.3);
        }
        .info-panel h3 {
            color: #F59E0B;
            margin-bottom: 15px;
        }
        .equation {
            background: rgba(30, 41, 59, 0.6);
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            text-align: center;
            font-size: 1.1em;
            color: #22C55E;
            font-family: 'Courier New', monospace;
        }
        .description {
            line-height: 1.8;
            color: #CBD5E1;
        }
        .legend {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 15px;
        }
        .legend-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 8px;
            background: rgba(30, 41, 59, 0.5);
            border-radius: 5px;
        }
        .legend-color {
            width: 30px;
            height: 30px;
            border-radius: 5px;
            border: 2px solid rgba(255, 255, 255, 0.3);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧪 酶活性与米氏方程模拟器</h1>

        <div class="main-content">
            <div class="canvas-section">
                <h3>酶促反应动画</h3>
                <canvas id="reactionCanvas"></canvas>
            </div>

            <div class="canvas-section">
                <h3>米氏方程曲线 (V vs [S])</h3>
                <canvas id="kineticsCanvas"></canvas>
            </div>
        </div>

        <div class="main-content">
            <div class="control-panel">
                <div class="control-group">
                    <h3>反应参数</h3>

                    <div class="slider-group">
                        <label>底物浓度 [S]: <span id="substrateValue">5.0</span> mM</label>
                        <input type="range" id="substrateSlider" min="0.1" max="20" step="0.1" value="5">
                    </div>

                    <div class="slider-group">
                        <label>酶浓度 [E]: <span id="enzymeValue">1.0</span> µM</label>
                        <input type="range" id="enzymeSlider" min="0.1" max="3" step="0.1" value="1">
                    </div>

                    <div class="slider-group">
                        <label>Vmax: <span id="vmaxValue">10.0</span> µmol/min</label>
                        <input type="range" id="vmaxSlider" min="5" max="20" step="0.5" value="10">
                    </div>

                    <div class="slider-group">
                        <label>Km: <span id="kmValue">5.0</span> mM</label>
                        <input type="range" id="kmSlider" min="1" max="15" step="0.5" value="5">
                    </div>
                </div>

                <div class="control-group">
                    <h3>环境因素</h3>

                    <div class="slider-group">
                        <label>温度: <span id="tempValue">37</span> °C</label>
                        <input type="range" id="tempSlider" min="0" max="80" step="1" value="37">
                    </div>

                    <div class="slider-group">
                        <label>pH: <span id="phValue">7.0</span></label>
                        <input type="range" id="phSlider" min="2" max="12" step="0.1" value="7">
                    </div>
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <button id="playPauseBtn" onclick="togglePlayPause()">⏸️ 暂停</button>
                    <button onclick="resetSimulation()">🔄 重置参数</button>
                </div>

                <div class="stats">
                    <div class="stat-item">
                        <span class="stat-label">当前反应速率 (V)</span>
                        <span class="stat-value" id="currentRate">5.0</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">相对活性</span>
                        <span class="stat-value" id="relativeActivity">100%</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">效率 (V/Vmax)</span>
                        <span class="stat-value" id="efficiency">50%</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">产物生成</span>
                        <span class="stat-value" id="productCount">0</span>
                    </div>
                </div>
            </div>

            <div class="info-panel">
                <h3>米氏方程</h3>
                <div class="equation">
                    V = (Vmax × [S]) / (Km + [S])
                </div>

                <div class="description">
                    <strong style="color: #22C55E;">参数说明：</strong><br>
                    • <strong>V</strong>: 反应速率 (µmol/min)<br>
                    • <strong>Vmax</strong>: 最大反应速率，所有酶被底物饱和时的速率<br>
                    • <strong>[S]</strong>: 底物浓度 (mM)<br>
                    • <strong>Km</strong>: 米氏常数，反应速率达到Vmax一半时的底物浓度<br>
                    <br>
                    <strong style="color: #EC4899;">环境影响：</strong><br>
                    • <strong>温度</strong>: 最适温度约37°C，过高或过低都会降低活性<br>
                    • <strong>pH</strong>: 最适pH约7.0，偏离最适pH会影响酶的构象和活性<br>
                </div>

                <div class="legend">
                    <div class="legend-item">
                        <div class="legend-color" style="background: #3B82F6;"></div>
                        <span>酶 (E)</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #F59E0B;"></div>
                        <span>底物 (S)</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #EC4899;"></div>
                        <span>酶-底物复合物 (ES)</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #22C55E;"></div>
                        <span>产物 (P)</span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const reactionCanvas = document.getElementById('reactionCanvas');
        const kineticsCanvas = document.getElementById('kineticsCanvas');
        const rCtx = reactionCanvas.getContext('2d');
        const kCtx = kineticsCanvas.getContext('2d');

        reactionCanvas.width = reactionCanvas.offsetWidth;
        reactionCanvas.height = reactionCanvas.offsetHeight;
        kineticsCanvas.width = kineticsCanvas.offsetWidth;
        kineticsCanvas.height = kineticsCanvas.offsetHeight;

        const COLORS = {
            primary: '#22C55E',
            secondary: '#EC4899',
            accent: '#F59E0B',
            enzyme: '#3B82F6',
            substrate: '#F59E0B',
            complex: '#EC4899',
            product: '#22C55E'
        };

        let substrateConc = 5.0;
        let enzymeConc = 1.0;
        let vmax = 10.0;
        let km = 5.0;
        let temperature = 37;
        let pH = 7.0;
        let productCount = 0;
        let isPaused = false;

        class Particle {
            constructor(x, y, type) {
                this.x = x;
                this.y = y;
                this.vx = (Math.random() - 0.5) * 2;
                this.vy = (Math.random() - 0.5) * 2;
                this.type = type;
                this.radius = type === 'enzyme' ? 20 : 12;
                this.bound = null;
                this.reactionTime = 0;
            }

            update(width, height) {
                if (this.bound) {
                    this.reactionTime++;
                    if (this.reactionTime > 60) {
                        return 'complete';
                    }
                    return null;
                }

                this.x += this.vx * getSpeedMultiplier();
                this.y += this.vy * getSpeedMultiplier();

                if (this.x < this.radius || this.x > width - this.radius) {
                    this.vx *= -1;
                    this.x = Math.max(this.radius, Math.min(width - this.radius, this.x));
                }
                if (this.y < this.radius || this.y > height - this.radius) {
                    this.vy *= -1;
                    this.y = Math.max(this.radius, Math.min(height - this.radius, this.y));
                }

                return null;
            }

            draw(ctx) {
                ctx.save();

                if (this.type === 'enzyme') {
                    // 绘制酶（蓝色，带活性位点）
                    ctx.fillStyle = this.bound ? COLORS.complex : COLORS.enzyme;
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                    ctx.fill();

                    // 活性位点
                    if (!this.bound) {
                        ctx.fillStyle = '#1E293B';
                        ctx.beginPath();
                        ctx.arc(this.x, this.y, 8, 0, Math.PI * 2);
                        ctx.fill();
                    }

                    ctx.strokeStyle = '#FFF';
                    ctx.lineWidth = 2;
                    ctx.stroke();
                } else if (this.type === 'substrate') {
                    // 绘制底物（橙色）
                    ctx.fillStyle = COLORS.substrate;
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                    ctx.fill();

                    ctx.strokeStyle = '#FFF';
                    ctx.lineWidth = 2;
                    ctx.stroke();
                } else if (this.type === 'product') {
                    // 绘制产物（绿色）
                    ctx.fillStyle = COLORS.product;
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                    ctx.fill();

                    ctx.strokeStyle = '#FFF';
                    ctx.lineWidth = 2;
                    ctx.stroke();
                }

                // 绘制标签
                ctx.fillStyle = '#FFF';
                ctx.font = 'bold 12px Arial';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                if (this.type === 'enzyme') {
                    ctx.fillText(this.bound ? 'ES' : 'E', this.x, this.y);
                } else if (this.type === 'substrate') {
                    ctx.fillText('S', this.x, this.y);
                } else {
                    ctx.fillText('P', this.x, this.y);
                }

                ctx.restore();
            }
        }

        let enzymes = [];
        let substrates = [];
        let products = [];

        function initParticles() {
            enzymes = [];
            substrates = [];
            products = [];
            productCount = 0;

            const enzymeCount = Math.ceil(enzymeConc * 3);
            const substrateCount = Math.ceil(substrateConc * 2);

            for (let i = 0; i < enzymeCount; i++) {
                enzymes.push(new Particle(
                    Math.random() * (reactionCanvas.width - 40) + 20,
                    Math.random() * (reactionCanvas.height - 40) + 20,
                    'enzyme'
                ));
            }

            for (let i = 0; i < substrateCount; i++) {
                substrates.push(new Particle(
                    Math.random() * (reactionCanvas.width - 24) + 12,
                    Math.random() * (reactionCanvas.height - 24) + 12,
                    'substrate'
                ));
            }
        }

        function getSpeedMultiplier() {
            // 温度影响速率（最适温度37°C）
            const tempFactor = Math.exp(-Math.pow((temperature - 37) / 20, 2));

            // pH影响速率（最适pH 7.0）
            const phFactor = Math.exp(-Math.pow((pH - 7) / 2, 2));

            return tempFactor * phFactor;
        }

        function getRelativeActivity() {
            return Math.round(getSpeedMultiplier() * 100);
        }

        function calculateReactionRate() {
            const baseRate = (vmax * substrateConc) / (km + substrateConc);
            return baseRate * getSpeedMultiplier();
        }

        function checkCollisions() {
            enzymes.forEach(enzyme => {
                if (enzyme.bound) return;

                substrates.forEach((substrate, idx) => {
                    const dx = enzyme.x - substrate.x;
                    const dy = enzyme.y - substrate.y;
                    const distance = Math.sqrt(dx * dx + dy * dy);

                    if (distance < enzyme.radius + substrate.radius) {
                        // 发生碰撞，形成ES复合物
                        if (Math.random() < getSpeedMultiplier()) {
                            enzyme.bound = substrate;
                            substrate.x = enzyme.x;
                            substrate.y = enzyme.y;
                            substrate.vx = 0;
                            substrate.vy = 0;
                        }
                    }
                });
            });
        }

        function updateReaction() {
            checkCollisions();

            enzymes.forEach(enzyme => {
                const result = enzyme.update(reactionCanvas.width, reactionCanvas.height);

                if (result === 'complete' && enzyme.bound) {
                    // 反应完成，生成产物
                    const product = new Particle(enzyme.x + 30, enzyme.y, 'product');
                    products.push(product);
                    productCount++;

                    // 移除底物
                    const substrateIdx = substrates.indexOf(enzyme.bound);
                    if (substrateIdx > -1) {
                        substrates.splice(substrateIdx, 1);
                    }

                    // 释放酶
                    enzyme.bound = null;
                    enzyme.reactionTime = 0;
                }
            });

            substrates = substrates.filter(s => !enzymes.some(e => e.bound === s));
            substrates.forEach(s => s.update(reactionCanvas.width, reactionCanvas.height));
            products.forEach(p => p.update(reactionCanvas.width, reactionCanvas.height));
        }

        function drawReaction() {
            rCtx.clearRect(0, 0, reactionCanvas.width, reactionCanvas.height);

            // 绘制背景
            rCtx.fillStyle = 'rgba(148, 163, 184, 0.05)';
            rCtx.fillRect(0, 0, reactionCanvas.width, reactionCanvas.height);

            // 绘制所有粒子
            substrates.forEach(s => s.draw(rCtx));
            products.forEach(p => p.draw(rCtx));
            enzymes.forEach(e => {
                e.draw(rCtx);
                if (e.bound) {
                    // 绘制ES复合物的连接线
                    rCtx.strokeStyle = COLORS.complex;
                    rCtx.lineWidth = 3;
                    rCtx.setLineDash([5, 5]);
                    rCtx.beginPath();
                    rCtx.arc(e.x, e.y, e.radius + 5, 0, Math.PI * 2);
                    rCtx.stroke();
                    rCtx.setLineDash([]);
                }
            });
        }

        function drawKineticsCurve() {
            kCtx.clearRect(0, 0, kineticsCanvas.width, kineticsCanvas.height);

            const padding = 60;
            const width = kineticsCanvas.width - 2 * padding;
            const height = kineticsCanvas.height - 2 * padding;

            // 绘制坐标轴
            kCtx.strokeStyle = '#94A3B8';
            kCtx.lineWidth = 2;

            // Y轴
            kCtx.beginPath();
            kCtx.moveTo(padding, padding);
            kCtx.lineTo(padding, padding + height);
            kCtx.stroke();

            // X轴
            kCtx.beginPath();
            kCtx.moveTo(padding, padding + height);
            kCtx.lineTo(padding + width, padding + height);
            kCtx.stroke();

            // 绘制标签
            kCtx.fillStyle = '#F1F5F9';
            kCtx.font = 'bold 14px Arial';
            kCtx.textAlign = 'center';
            kCtx.fillText('[S] (mM)', padding + width / 2, kineticsCanvas.height - 20);

            kCtx.save();
            kCtx.translate(20, padding + height / 2);
            kCtx.rotate(-Math.PI / 2);
            kCtx.fillText('V (µmol/min)', 0, 0);
            kCtx.restore();

            // 绘制网格线和刻度
            kCtx.strokeStyle = 'rgba(148, 163, 184, 0.2)';
            kCtx.lineWidth = 1;
            kCtx.fillStyle = '#94A3B8';
            kCtx.font = '12px Arial';

            const maxS = 20;
            const maxV = vmax * 1.1;

            // X轴刻度
            for (let i = 0; i <= 5; i++) {
                const x = padding + (width / 5) * i;
                const value = (maxS / 5) * i;

                kCtx.beginPath();
                kCtx.moveTo(x, padding + height);
                kCtx.lineTo(x, padding);
                kCtx.stroke();

                kCtx.textAlign = 'center';
                kCtx.fillText(value.toFixed(1), x, padding + height + 20);
            }

            // Y轴刻度
            for (let i = 0; i <= 5; i++) {
                const y = padding + height - (height / 5) * i;
                const value = (maxV / 5) * i;

                kCtx.beginPath();
                kCtx.moveTo(padding, y);
                kCtx.lineTo(padding + width, y);
                kCtx.stroke();

                kCtx.textAlign = 'right';
                kCtx.fillText(value.toFixed(1), padding - 10, y + 5);
            }

            // 绘制Vmax线
            const vmaxY = padding + height - (vmax / maxV) * height;
            kCtx.strokeStyle = COLORS.secondary;
            kCtx.lineWidth = 2;
            kCtx.setLineDash([10, 5]);
            kCtx.beginPath();
            kCtx.moveTo(padding, vmaxY);
            kCtx.lineTo(padding + width, vmaxY);
            kCtx.stroke();
            kCtx.setLineDash([]);

            kCtx.fillStyle = COLORS.secondary;
            kCtx.textAlign = 'left';
            kCtx.fillText('Vmax', padding + width + 10, vmaxY + 5);

            // 绘制Km线
            const kmX = padding + (km / maxS) * width;
            kCtx.strokeStyle = COLORS.accent;
            kCtx.lineWidth = 2;
            kCtx.setLineDash([10, 5]);
            kCtx.beginPath();
            kCtx.moveTo(kmX, padding);
            kCtx.lineTo(kmX, padding + height);
            kCtx.stroke();
            kCtx.setLineDash([]);

            kCtx.fillStyle = COLORS.accent;
            kCtx.textAlign = 'center';
            kCtx.fillText('Km', kmX, padding - 10);

            // 绘制米氏曲线
            kCtx.strokeStyle = COLORS.primary;
            kCtx.lineWidth = 3;
            kCtx.beginPath();

            for (let s = 0; s <= maxS; s += 0.1) {
                const v = (vmax * s) / (km + s);
                const x = padding + (s / maxS) * width;
                const y = padding + height - (v / maxV) * height;

                if (s === 0) {
                    kCtx.moveTo(x, y);
                } else {
                    kCtx.lineTo(x, y);
                }
            }
            kCtx.stroke();

            // 绘制当前点
            const currentV = calculateReactionRate();
            const currentX = padding + (substrateConc / maxS) * width;
            const currentY = padding + height - (currentV / maxV) * height;

            kCtx.fillStyle = COLORS.secondary;
            kCtx.beginPath();
            kCtx.arc(currentX, currentY, 8, 0, Math.PI * 2);
            kCtx.fill();

            kCtx.strokeStyle = '#FFF';
            kCtx.lineWidth = 2;
            kCtx.stroke();
        }

        function updateStats() {
            const currentV = calculateReactionRate();
            const efficiency = (currentV / vmax) * 100;

            document.getElementById('currentRate').textContent = currentV.toFixed(2) + ' µmol/min';
            document.getElementById('relativeActivity').textContent = getRelativeActivity() + '%';
            document.getElementById('efficiency').textContent = efficiency.toFixed(1) + '%';
            document.getElementById('productCount').textContent = productCount;
        }

        function animate() {
            if (!isPaused) {
                updateReaction();
            }
            drawReaction();
            drawKineticsCurve();
            updateStats();
            requestAnimationFrame(animate);
        }

        function resetSimulation() {
            substrateConc = 5.0;
            enzymeConc = 1.0;
            vmax = 10.0;
            km = 5.0;
            temperature = 37;
            pH = 7.0;

            document.getElementById('substrateSlider').value = 5;
            document.getElementById('enzymeSlider').value = 1;
            document.getElementById('vmaxSlider').value = 10;
            document.getElementById('kmSlider').value = 5;
            document.getElementById('tempSlider').value = 37;
            document.getElementById('phSlider').value = 7;

            updateSliderValues();
            initParticles();
        }

        function togglePlayPause() {
            isPaused = !isPaused;
            const btn = document.getElementById('playPauseBtn');
            btn.textContent = isPaused ? '▶️ 播放' : '⏸️ 暂停';
        }

        function updateSliderValues() {
            document.getElementById('substrateValue').textContent = substrateConc.toFixed(1);
            document.getElementById('enzymeValue').textContent = enzymeConc.toFixed(1);
            document.getElementById('vmaxValue').textContent = vmax.toFixed(1);
            document.getElementById('kmValue').textContent = km.toFixed(1);
            document.getElementById('tempValue').textContent = temperature;
            document.getElementById('phValue').textContent = pH.toFixed(1);
        }

        // 事件监听器
        document.getElementById('substrateSlider').addEventListener('input', (e) => {
            substrateConc = parseFloat(e.target.value);
            updateSliderValues();
            initParticles();
        });

        document.getElementById('enzymeSlider').addEventListener('input', (e) => {
            enzymeConc = parseFloat(e.target.value);
            updateSliderValues();
            initParticles();
        });

        document.getElementById('vmaxSlider').addEventListener('input', (e) => {
            vmax = parseFloat(e.target.value);
            updateSliderValues();
        });

        document.getElementById('kmSlider').addEventListener('input', (e) => {
            km = parseFloat(e.target.value);
            updateSliderValues();
        });

        document.getElementById('tempSlider').addEventListener('input', (e) => {
            temperature = parseInt(e.target.value);
            updateSliderValues();
        });

        document.getElementById('phSlider').addEventListener('input', (e) => {
            pH = parseFloat(e.target.value);
            updateSliderValues();
        });

        // 初始化
        initParticles();
        updateSliderValues();
        animate();

        // 响应式调整
        window.addEventListener('resize', () => {
            reactionCanvas.width = reactionCanvas.offsetWidth;
            reactionCanvas.height = reactionCanvas.offsetHeight;
            kineticsCanvas.width = kineticsCanvas.offsetWidth;
            kineticsCanvas.height = kineticsCanvas.offsetHeight;
            initParticles();
        });
    </script>
</body>
</html>
$HTML$,
 75,
 34,
 796,
 false,
 0,
 NOW(),
 '{"name": "酶活性与米氏方程", "description": "酶催化反应的动力学模拟，展示底物浓度对反应速率的影响", "difficulty": "medium", "render_mode": "html"}');


-- [7/24] 电子轨道 (chemistry, 75分)
INSERT INTO simulator_templates
(subject, topic, code, quality_score, visual_elements, line_count, has_setup_update, variable_count, created_at, metadata)
VALUES
('chemistry',
 '电子轨道',
 $HTML$<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>电子轨道 - 化学交互模拟器</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
            color: #F1F5F9;
            min-height: 100vh;
            padding: 20px;
            overflow-x: hidden;
        }

        .container {
            max-width: 1600px;
            margin: 0 auto;
        }

        header {
            text-align: center;
            margin-bottom: 30px;
            animation: fadeInDown 0.6s ease-out;
        }

        h1 {
            font-size: 2.5em;
            color: #DC2626;
            margin-bottom: 10px;
            text-shadow: 0 2px 10px rgba(220, 38, 38, 0.3);
        }

        .subtitle {
            font-size: 1.1em;
            color: #94A3B8;
        }

        .main-grid {
            display: grid;
            grid-template-columns: 320px 1fr 320px;
            gap: 20px;
            animation: fadeIn 0.8s ease-out;
        }

        .panel {
            background: rgba(30, 41, 59, 0.8);
            border: 2px solid rgba(220, 38, 38, 0.3);
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(10px);
            height: fit-content;
        }

        .panel-section {
            margin-bottom: 25px;
        }

        .panel-section:last-child {
            margin-bottom: 0;
        }

        .panel-section h3 {
            color: #DC2626;
            font-size: 1.2em;
            margin-bottom: 15px;
            border-bottom: 2px solid rgba(220, 38, 38, 0.3);
            padding-bottom: 8px;
        }

        .orbital-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-bottom: 15px;
        }

        .orbital-btn {
            background: linear-gradient(135deg, rgba(220, 38, 38, 0.2), rgba(220, 38, 38, 0.1));
            border: 2px solid rgba(220, 38, 38, 0.3);
            color: #F1F5F9;
            padding: 12px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 0.95em;
            font-weight: 500;
            text-align: center;
        }

        .orbital-btn:hover {
            background: linear-gradient(135deg, rgba(220, 38, 38, 0.4), rgba(220, 38, 38, 0.2));
            border-color: #DC2626;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(220, 38, 38, 0.3);
        }

        .orbital-btn.active {
            background: linear-gradient(135deg, #DC2626, #B91C1C);
            border-color: #DC2626;
            box-shadow: 0 5px 20px rgba(220, 38, 38, 0.4);
        }

        .slider-group {
            margin-bottom: 20px;
        }

        .slider-label {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 0.95em;
            color: #CBD5E1;
        }

        .slider-value {
            color: #DC2626;
            font-weight: 600;
        }

        input[type="range"] {
            width: 100%;
            height: 6px;
            border-radius: 3px;
            background: linear-gradient(90deg, rgba(220, 38, 38, 0.3), rgba(220, 38, 38, 0.6));
            outline: none;
            -webkit-appearance: none;
        }

        input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: #DC2626;
            cursor: pointer;
            box-shadow: 0 2px 8px rgba(220, 38, 38, 0.4);
            transition: all 0.3s ease;
        }

        input[type="range"]::-webkit-slider-thumb:hover {
            transform: scale(1.2);
            box-shadow: 0 3px 12px rgba(220, 38, 38, 0.6);
        }

        .checkbox-group {
            display: flex;
            align-items: center;
            margin-bottom: 12px;
            cursor: pointer;
        }

        .checkbox-group input[type="checkbox"] {
            width: 20px;
            height: 20px;
            margin-right: 10px;
            cursor: pointer;
            accent-color: #DC2626;
        }

        .info-box {
            background: rgba(37, 99, 235, 0.1);
            border: 2px solid rgba(37, 99, 235, 0.3);
            border-radius: 10px;
            padding: 15px;
        }

        .info-box h4 {
            color: #2563EB;
            margin-bottom: 10px;
            font-size: 1.05em;
        }

        .info-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 0.9em;
        }

        .info-label {
            color: #94A3B8;
        }

        .info-value {
            color: #10B981;
            font-weight: 600;
        }

        .energy-diagram {
            background: rgba(15, 23, 42, 0.6);
            border-radius: 10px;
            padding: 20px;
            margin-top: 15px;
        }

        .energy-level {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
            position: relative;
        }

        .energy-label {
            width: 40px;
            font-size: 0.9em;
            color: #CBD5E1;
        }

        .energy-bar {
            flex: 1;
            height: 3px;
            background: #2563EB;
            border-radius: 2px;
            position: relative;
        }

        .electron-dot {
            width: 12px;
            height: 12px;
            background: #DC2626;
            border-radius: 50%;
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            box-shadow: 0 0 10px rgba(220, 38, 38, 0.6);
            animation: pulse 2s ease-in-out infinite;
        }

        .spectrum-display {
            background: rgba(15, 23, 42, 0.6);
            border-radius: 10px;
            padding: 15px;
            margin-top: 15px;
        }

        .spectrum-bar {
            height: 40px;
            background: linear-gradient(90deg,
                #FF0000 0%, #FF7F00 14%, #FFFF00 28%,
                #00FF00 42%, #0000FF 57%, #4B0082 71%,
                #9400D3 85%, #FF00FF 100%);
            border-radius: 5px;
            position: relative;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        }

        .spectrum-marker {
            position: absolute;
            top: -10px;
            width: 3px;
            height: 60px;
            background: #F1F5F9;
            box-shadow: 0 0 10px rgba(241, 245, 249, 0.8);
        }

        .canvas-container {
            background: rgba(15, 23, 42, 0.6);
            border: 2px solid rgba(220, 38, 38, 0.3);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            position: relative;
        }

        #orbitalCanvas {
            width: 100%;
            height: 700px;
            border-radius: 10px;
            background: radial-gradient(circle at center, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.9));
            cursor: grab;
        }

        #orbitalCanvas:active {
            cursor: grabbing;
        }

        .quantum-numbers {
            position: absolute;
            top: 20px;
            left: 20px;
            background: rgba(30, 41, 59, 0.95);
            border: 2px solid rgba(220, 38, 38, 0.4);
            border-radius: 10px;
            padding: 15px;
            backdrop-filter: blur(10px);
        }

        .quantum-numbers h4 {
            color: #DC2626;
            margin-bottom: 10px;
            font-size: 1.05em;
        }

        .quantum-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 6px;
            font-size: 0.9em;
        }

        .quantum-item span:first-child {
            color: #94A3B8;
            margin-right: 15px;
        }

        .quantum-item span:last-child {
            color: #10B981;
            font-weight: 600;
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes pulse {
            0%, 100% {
                transform: translateY(-50%) scale(1);
                opacity: 1;
            }
            50% {
                transform: translateY(-50%) scale(1.3);
                opacity: 0.7;
            }
        }

        @media (max-width: 1400px) {
            .main-grid {
                grid-template-columns: 1fr;
            }

            .quantum-numbers {
                position: static;
                margin-bottom: 15px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>⚛️ 电子轨道可视化模拟器</h1>
            <p class="subtitle">探索量子力学与原子结构</p>
        </header>

        <div class="main-grid">
            <aside class="panel">
                <div class="panel-section">
                    <h3>轨道类型</h3>
                    <div class="orbital-grid">
                        <button class="orbital-btn active" data-orbital="1s">1s</button>
                        <button class="orbital-btn" data-orbital="2s">2s</button>
                        <button class="orbital-btn" data-orbital="2px">2p<sub>x</sub></button>
                        <button class="orbital-btn" data-orbital="2py">2p<sub>y</sub></button>
                        <button class="orbital-btn" data-orbital="2pz">2p<sub>z</sub></button>
                        <button class="orbital-btn" data-orbital="3s">3s</button>
                        <button class="orbital-btn" data-orbital="3dz2">3d<sub>z²</sub></button>
                        <button class="orbital-btn" data-orbital="3dxy">3d<sub>xy</sub></button>
                    </div>
                </div>

                <div class="panel-section">
                    <h3>视图控制</h3>
                    <div class="slider-group">
                        <div class="slider-label">
                            <span>旋转速度</span>
                            <span class="slider-value" id="rotationValue">1.0°/帧</span>
                        </div>
                        <input type="range" id="rotationSpeed" min="0" max="3" step="0.1" value="1">
                    </div>

                    <div class="slider-group">
                        <div class="slider-label">
                            <span>电子云密度</span>
                            <span class="slider-value" id="densityValue">100%</span>
                        </div>
                        <input type="range" id="density" min="20" max="200" step="10" value="100">
                    </div>

                    <div class="slider-group">
                        <div class="slider-label">
                            <span>透明度</span>
                            <span class="slider-value" id="opacityValue">70%</span>
                        </div>
                        <input type="range" id="opacity" min="10" max="100" step="5" value="70">
                    </div>
                </div>

                <div class="panel-section">
                    <h3>显示选项</h3>
                    <label class="checkbox-group">
                        <input type="checkbox" id="showElectronCloud" checked>
                        <span>电子云</span>
                    </label>
                    <label class="checkbox-group">
                        <input type="checkbox" id="showAxes" checked>
                        <span>坐标轴</span>
                    </label>
                    <label class="checkbox-group">
                        <input type="checkbox" id="showNodes" checked>
                        <span>节点面</span>
                    </label>
                    <label class="checkbox-group">
                        <input type="checkbox" id="animateElectrons">
                        <span>电子运动</span>
                    </label>
                </div>

                <div class="info-box">
                    <h4>量子数</h4>
                    <div class="info-item">
                        <span class="info-label">主量子数 n:</span>
                        <span class="info-value" id="quantumN">1</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">角量子数 l:</span>
                        <span class="info-value" id="quantumL">0</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">磁量子数 m:</span>
                        <span class="info-value" id="quantumM">0</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">轨道形状:</span>
                        <span class="info-value" id="orbitalShape">球形</span>
                    </div>
                </div>

                <div class="energy-diagram">
                    <h4 style="color: #2563EB; margin-bottom: 15px;">能级图</h4>
                    <div class="energy-level">
                        <span class="energy-label">3d</span>
                        <div class="energy-bar" style="width: 85%;"></div>
                    </div>
                    <div class="energy-level">
                        <span class="energy-label">3p</span>
                        <div class="energy-bar" style="width: 70%;"></div>
                    </div>
                    <div class="energy-level">
                        <span class="energy-label">3s</span>
                        <div class="energy-bar" style="width: 65%;"></div>
                    </div>
                    <div class="energy-level">
                        <span class="energy-label">2p</span>
                        <div class="energy-bar" style="width: 50%;"></div>
                    </div>
                    <div class="energy-level">
                        <span class="energy-label">2s</span>
                        <div class="energy-bar" style="width: 40%;"></div>
                    </div>
                    <div class="energy-level" id="currentEnergyLevel">
                        <span class="energy-label">1s</span>
                        <div class="energy-bar" style="width: 25%;">
                            <div class="electron-dot" style="left: calc(100% - 6px);"></div>
                        </div>
                    </div>
                </div>
            </aside>

            <main class="canvas-container">
                <div class="quantum-numbers">
                    <h4>轨道信息</h4>
                    <div class="quantum-item">
                        <span>轨道名称:</span>
                        <span id="orbitalName">1s</span>
                    </div>
                    <div class="quantum-item">
                        <span>电子容量:</span>
                        <span id="electronCapacity">2</span>
                    </div>
                    <div class="quantum-item">
                        <span>节点数:</span>
                        <span id="nodeCount">0</span>
                    </div>
                </div>
                <canvas id="orbitalCanvas"></canvas>
            </main>

            <aside class="panel">
                <div class="panel-section">
                    <h3>能级跃迁</h3>
                    <div class="slider-group">
                        <div class="slider-label">
                            <span>起始能级</span>
                            <span class="slider-value" id="startLevel">n=1</span>
                        </div>
                        <input type="range" id="startLevelSlider" min="1" max="5" step="1" value="1">
                    </div>

                    <div class="slider-group">
                        <div class="slider-label">
                            <span>终止能级</span>
                            <span class="slider-value" id="endLevel">n=2</span>
                        </div>
                        <input type="range" id="endLevelSlider" min="1" max="5" step="1" value="2">
                    </div>

                    <button class="orbital-btn" id="transitionBtn" style="grid-column: span 2; margin-top: 10px;">
                        模拟跃迁
                    </button>
                </div>

                <div class="info-box" style="margin-top: 20px;">
                    <h4>跃迁信息</h4>
                    <div class="info-item">
                        <span class="info-label">能量变化:</span>
                        <span class="info-value" id="energyChange">-10.2 eV</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">光子波长:</span>
                        <span class="info-value" id="wavelength">121.5 nm</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">光谱区:</span>
                        <span class="info-value" id="spectrumRegion">紫外</span>
                    </div>
                </div>

                <div class="spectrum-display">
                    <h4 style="color: #2563EB; margin-bottom: 10px;">发射光谱</h4>
                    <div class="spectrum-bar">
                        <div class="spectrum-marker" id="spectrumMarker" style="left: 10%;"></div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 8px; font-size: 0.85em; color: #94A3B8;">
                        <span>380nm</span>
                        <span>可见光</span>
                        <span>750nm</span>
                    </div>
                </div>

                <div class="panel-section" style="margin-top: 20px;">
                    <h3>轨道描述</h3>
                    <div style="font-size: 0.9em; line-height: 1.6; color: #CBD5E1;">
                        <p id="orbitalDescription">
                            <strong>1s轨道</strong>是最低能级的原子轨道，呈球形对称分布。
                            电子出现概率在原子核附近最大，随距离增加而指数衰减。
                            该轨道无节点面，可容纳最多2个自旋相反的电子。
                        </p>
                    </div>
                </div>

                <div class="info-box" style="margin-top: 15px;">
                    <h4>经典应用</h4>
                    <div style="font-size: 0.85em; line-height: 1.5; color: #94A3B8; margin-top: 10px;">
                        • 化学键形成<br>
                        • 分子轨道理论<br>
                        • 光谱分析<br>
                        • 量子计算
                    </div>
                </div>
            </aside>
        </div>
    </div>

    <script>
        const COLORS = {
            primary: '#DC2626',
            secondary: '#2563EB',
            accent: '#10B981',
            background: '#1E293B',
            text: '#F1F5F9'
        };

        const ORBITAL_DATA = {
            '1s': {
                n: 1, l: 0, m: 0,
                shape: '球形',
                capacity: 2,
                nodes: 0,
                description: '<strong>1s轨道</strong>是最低能级的原子轨道，呈球形对称分布。电子出现概率在原子核附近最大，随距离增加而指数衰减。该轨道无节点面，可容纳最多2个自旋相反的电子。'
            },
            '2s': {
                n: 2, l: 0, m: 0,
                shape: '球形',
                capacity: 2,
                nodes: 1,
                description: '<strong>2s轨道</strong>是第二能级的s轨道，同样呈球形对称。与1s不同，2s轨道具有一个球形节点面，电子云分为内外两层，外层概率密度较大。'
            },
            '2px': {
                n: 2, l: 1, m: -1,
                shape: '哑铃形',
                capacity: 2,
                nodes: 1,
                description: '<strong>2p<sub>x</sub>轨道</strong>沿x轴方向延伸，呈哑铃形。在yz平面存在一个节点面，电子云主要分布在x轴正负两侧，参与形成σ键和π键。'
            },
            '2py': {
                n: 2, l: 1, m: 0,
                shape: '哑铃形',
                capacity: 2,
                nodes: 1,
                description: '<strong>2p<sub>y</sub>轨道</strong>沿y轴方向延伸，与2p<sub>x</sub>结构相似但方向垂直。在xz平面有节点面，与2p<sub>x</sub>和2p<sub>z</sub>能量简并。'
            },
            '2pz': {
                n: 2, l: 1, m: 1,
                shape: '哑铃形',
                capacity: 2,
                nodes: 1,
                description: '<strong>2p<sub>z</sub>轨道</strong>沿z轴方向延伸，形成哑铃状电子云。在xy平面为节点面，常参与形成π键和配位键。'
            },
            '3s': {
                n: 3, l: 0, m: 0,
                shape: '球形',
                capacity: 2,
                nodes: 2,
                description: '<strong>3s轨道</strong>是第三能级的s轨道，具有两个球形节点面，电子云分为三层。最外层概率密度最大，能量高于1s和2s轨道。'
            },
            '3dz2': {
                n: 3, l: 2, m: 0,
                shape: '双球体',
                capacity: 2,
                nodes: 2,
                description: '<strong>3d<sub>z²</sub>轨道</strong>具有独特的形状，沿z轴为两个锥形加中间环状电子云。在过渡金属化学中起重要作用。'
            },
            '3dxy': {
                n: 3, l: 2, m: -2,
                shape: '四叶草形',
                capacity: 2,
                nodes: 2,
                description: '<strong>3d<sub>xy</sub>轨道</strong>在xy平面内呈四叶草形分布，电子云主要集中在四个象限。xz和yz平面为节点面。'
            }
        };

        class Point3D {
            constructor(x, y, z) {
                this.x = x;
                this.y = y;
                this.z = z;
            }

            rotateX(angle) {
                const cos = Math.cos(angle);
                const sin = Math.sin(angle);
                const y = this.y * cos - this.z * sin;
                const z = this.y * sin + this.z * cos;
                return new Point3D(this.x, y, z);
            }

            rotateY(angle) {
                const cos = Math.cos(angle);
                const sin = Math.sin(angle);
                const x = this.x * cos + this.z * sin;
                const z = -this.x * sin + this.z * cos;
                return new Point3D(x, this.y, z);
            }

            project(canvas, scale = 1) {
                const perspective = 600;
                const factor = perspective / (perspective + this.z);
                return {
                    x: canvas.width / 2 + this.x * scale * factor,
                    y: canvas.height / 2 + this.y * scale * factor,
                    z: this.z,
                    scale: factor
                };
            }
        }

        class OrbitalSimulator {
            constructor() {
                this.canvas = document.getElementById('orbitalCanvas');
                this.ctx = this.canvas.getContext('2d');
                this.setupCanvas();

                this.currentOrbital = '1s';
                this.rotationX = 0.3;
                this.rotationY = 0.3;
                this.rotationSpeed = 1.0;
                this.density = 100;
                this.opacity = 0.7;

                this.showElectronCloud = true;
                this.showAxes = true;
                this.showNodes = true;
                this.animateElectrons = false;

                this.isDragging = false;
                this.lastMouseX = 0;
                this.lastMouseY = 0;

                this.time = 0;

                this.setupEventListeners();
                this.updateOrbitalInfo();
                this.updateTransitionInfo(); // 初始化光谱标记位置
                this.animate();
            }

            setupCanvas() {
                const rect = this.canvas.getBoundingClientRect();
                this.canvas.width = rect.width * window.devicePixelRatio;
                this.canvas.height = rect.height * window.devicePixelRatio;
                this.ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
                this.width = rect.width;
                this.height = rect.height;
            }

            setupEventListeners() {
                // 轨道选择
                document.querySelectorAll('.orbital-btn').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        // 找到真正的按钮元素（可能点击到了子元素如<sub>）
                        const button = e.target.closest('.orbital-btn');
                        if (button && button.dataset.orbital) {
                            document.querySelectorAll('.orbital-btn').forEach(b => b.classList.remove('active'));
                            button.classList.add('active');
                            this.currentOrbital = button.dataset.orbital;
                            this.updateOrbitalInfo();
                        }
                    });
                });

                // 滑块控制
                document.getElementById('rotationSpeed').addEventListener('input', (e) => {
                    this.rotationSpeed = parseFloat(e.target.value);
                    document.getElementById('rotationValue').textContent = `${this.rotationSpeed.toFixed(1)}°/帧`;
                });

                document.getElementById('density').addEventListener('input', (e) => {
                    this.density = parseFloat(e.target.value);
                    document.getElementById('densityValue').textContent = `${e.target.value}%`;
                });

                document.getElementById('opacity').addEventListener('input', (e) => {
                    this.opacity = parseFloat(e.target.value) / 100;
                    document.getElementById('opacityValue').textContent = `${e.target.value}%`;
                });

                // 复选框
                document.getElementById('showElectronCloud').addEventListener('change', (e) => {
                    this.showElectronCloud = e.target.checked;
                });

                document.getElementById('showAxes').addEventListener('change', (e) => {
                    this.showAxes = e.target.checked;
                });

                document.getElementById('showNodes').addEventListener('change', (e) => {
                    this.showNodes = e.target.checked;
                });

                document.getElementById('animateElectrons').addEventListener('change', (e) => {
                    this.animateElectrons = e.target.checked;
                });

                // 鼠标拖动
                this.canvas.addEventListener('mousedown', (e) => {
                    this.isDragging = true;
                    this.lastMouseX = e.clientX;
                    this.lastMouseY = e.clientY;
                });

                this.canvas.addEventListener('mousemove', (e) => {
                    if (this.isDragging) {
                        const deltaX = e.clientX - this.lastMouseX;
                        const deltaY = e.clientY - this.lastMouseY;
                        this.rotationY += deltaX * 0.01;
                        this.rotationX += deltaY * 0.01;
                        this.lastMouseX = e.clientX;
                        this.lastMouseY = e.clientY;
                    }
                });

                this.canvas.addEventListener('mouseup', () => {
                    this.isDragging = false;
                });

                this.canvas.addEventListener('mouseleave', () => {
                    this.isDragging = false;
                });

                // 能级跃迁
                document.getElementById('startLevelSlider').addEventListener('input', (e) => {
                    document.getElementById('startLevel').textContent = `n=${e.target.value}`;
                    this.updateTransitionInfo();
                });

                document.getElementById('endLevelSlider').addEventListener('input', (e) => {
                    document.getElementById('endLevel').textContent = `n=${e.target.value}`;
                    this.updateTransitionInfo();
                });

                document.getElementById('transitionBtn').addEventListener('click', () => {
                    this.animateTransition();
                });

                window.addEventListener('resize', () => {
                    this.setupCanvas();
                });
            }

            updateOrbitalInfo() {
                const data = ORBITAL_DATA[this.currentOrbital];
                document.getElementById('quantumN').textContent = data.n;
                document.getElementById('quantumL').textContent = data.l;
                document.getElementById('quantumM').textContent = data.m;
                document.getElementById('orbitalShape').textContent = data.shape;
                document.getElementById('orbitalName').textContent = this.currentOrbital;
                document.getElementById('electronCapacity').textContent = data.capacity;
                document.getElementById('nodeCount').textContent = data.nodes;
                document.getElementById('orbitalDescription').innerHTML = data.description;

                // 更新能级图
                const energyLevels = document.querySelectorAll('.energy-level');
                energyLevels.forEach(level => {
                    const dot = level.querySelector('.electron-dot');
                    if (dot) dot.remove();
                });

                const orbitalMap = {
                    '1s': 5, '2s': 4, '2px': 3, '2py': 3, '2pz': 3,
                    '3s': 2, '3dz2': 0, '3dxy': 0
                };
                const levelIndex = orbitalMap[this.currentOrbital];
                if (levelIndex !== undefined) {
                    const targetLevel = energyLevels[levelIndex];
                    const bar = targetLevel.querySelector('.energy-bar');
                    const dot = document.createElement('div');
                    dot.className = 'electron-dot';
                    dot.style.left = 'calc(100% - 6px)';
                    bar.appendChild(dot);
                }
            }

            updateTransitionInfo() {
                const n1 = parseInt(document.getElementById('startLevelSlider').value);
                const n2 = parseInt(document.getElementById('endLevelSlider').value);

                // 氢原子能级公式: E = -13.6 * (1/n²) eV
                const E1 = -13.6 / (n1 * n1);
                const E2 = -13.6 / (n2 * n2);
                const deltaE = E2 - E1;

                document.getElementById('energyChange').textContent = `${deltaE.toFixed(2)} eV`;

                // 计算波长: λ = hc/ΔE
                const wavelength = Math.abs(1240 / deltaE); // nm
                document.getElementById('wavelength').textContent = `${wavelength.toFixed(1)} nm`;

                // 确定光谱区
                let region = '';
                if (wavelength < 380) region = '紫外';
                else if (wavelength <= 750) region = '可见光';
                else region = '红外';
                document.getElementById('spectrumRegion').textContent = region;

                // 更新光谱标记（将波长映射到光谱条上）
                const marker = document.getElementById('spectrumMarker');
                let position;

                if (wavelength < 380) {
                    // 紫外区：映射到0-10%
                    position = Math.max(0, Math.min(10, (wavelength / 380) * 10));
                    marker.style.background = '#8B5CF6'; // 紫色表示紫外
                } else if (wavelength <= 750) {
                    // 可见光区：映射到10-90%
                    position = 10 + ((wavelength - 380) / (750 - 380)) * 80;
                    // 根据波长设置颜色
                    const hue = 270 - ((wavelength - 380) / (750 - 380)) * 270;
                    marker.style.background = `hsl(${hue}, 80%, 60%)`;
                } else {
                    // 红外区：映射到90-100%
                    position = Math.min(100, 90 + ((wavelength - 750) / 750) * 10);
                    marker.style.background = '#DC2626'; // 红色表示红外
                }

                marker.style.left = `${position}%`;
            }

            animateTransition() {
                // 简单的视觉反馈
                const marker = document.getElementById('spectrumMarker');
                marker.style.transition = 'all 0.5s ease';
                marker.style.boxShadow = '0 0 20px rgba(220, 38, 38, 0.8)';
                setTimeout(() => {
                    marker.style.boxShadow = '0 0 10px rgba(241, 245, 249, 0.8)';
                }, 500);
            }

            drawAxes() {
                const scale = 150;
                const axes = [
                    { start: new Point3D(-scale, 0, 0), end: new Point3D(scale, 0, 0), color: COLORS.primary, label: 'X' },
                    { start: new Point3D(0, -scale, 0), end: new Point3D(0, scale, 0), color: COLORS.accent, label: 'Y' },
                    { start: new Point3D(0, 0, -scale), end: new Point3D(0, 0, scale), color: COLORS.secondary, label: 'Z' }
                ];

                axes.forEach(axis => {
                    const start = axis.start.rotateX(this.rotationX).rotateY(this.rotationY).project(this.canvas, 1);
                    const end = axis.end.rotateX(this.rotationX).rotateY(this.rotationY).project(this.canvas, 1);

                    this.ctx.strokeStyle = axis.color;
                    this.ctx.lineWidth = 2;
                    this.ctx.beginPath();
                    this.ctx.moveTo(start.x, start.y);
                    this.ctx.lineTo(end.x, end.y);
                    this.ctx.stroke();

                    // 标签
                    this.ctx.fillStyle = axis.color;
                    this.ctx.font = 'bold 14px Arial';
                    this.ctx.textAlign = 'center';
                    this.ctx.fillText(axis.label, end.x, end.y - 10);
                });
            }

            calculateOrbitalProbability(x, y, z) {
                const r = Math.sqrt(x * x + y * y + z * z);
                const theta = Math.acos(z / (r + 0.0001));
                const phi = Math.atan2(y, x);

                let prob = 0;

                switch (this.currentOrbital) {
                    case '1s':
                        prob = Math.exp(-2 * r);
                        break;
                    case '2s':
                        prob = (2 - r) * Math.exp(-r);
                        break;
                    case '2px':
                        prob = r * Math.exp(-r / 2) * Math.abs(Math.sin(theta) * Math.cos(phi));
                        break;
                    case '2py':
                        prob = r * Math.exp(-r / 2) * Math.abs(Math.sin(theta) * Math.sin(phi));
                        break;
                    case '2pz':
                        prob = r * Math.exp(-r / 2) * Math.abs(Math.cos(theta));
                        break;
                    case '3s':
                        prob = (27 - 18 * r + 2 * r * r) * Math.exp(-r / 1.5);
                        break;
                    case '3dz2':
                        prob = r * r * Math.exp(-r / 2.5) * Math.abs(3 * Math.cos(theta) * Math.cos(theta) - 1);
                        break;
                    case '3dxy':
                        prob = r * r * Math.exp(-r / 2.5) * Math.abs(Math.sin(theta) * Math.sin(theta) * Math.sin(2 * phi));
                        break;
                }

                return Math.max(0, prob);
            }

            drawOrbital() {
                if (!this.showElectronCloud) return;

                const points = [];
                const samples = Math.floor(this.density * 5);

                // 生成随机点
                for (let i = 0; i < samples; i++) {
                    const r = Math.random() * 5;
                    const theta = Math.random() * Math.PI;
                    const phi = Math.random() * 2 * Math.PI;

                    const x = r * Math.sin(theta) * Math.cos(phi);
                    const y = r * Math.sin(theta) * Math.sin(phi);
                    const z = r * Math.cos(theta);

                    const prob = this.calculateOrbitalProbability(x, y, z);

                    if (Math.random() < prob * 0.3) {
                        points.push(new Point3D(x * 30, y * 30, z * 30));
                    }
                }

                // 按z排序
                const rotatedPoints = points.map(p => ({
                    original: p,
                    rotated: p.rotateX(this.rotationX).rotateY(this.rotationY)
                }));

                rotatedPoints.sort((a, b) => a.rotated.z - b.rotated.z);

                // 绘制点
                rotatedPoints.forEach(({ original, rotated }) => {
                    const proj = rotated.project(this.canvas, 1);
                    const size = 2 * proj.scale;

                    const prob = this.calculateOrbitalProbability(
                        original.x / 30,
                        original.y / 30,
                        original.z / 30
                    );

                    const alpha = Math.min(1, prob * this.opacity);

                    this.ctx.fillStyle = `rgba(220, 38, 38, ${alpha})`;
                    this.ctx.beginPath();
                    this.ctx.arc(proj.x, proj.y, size, 0, Math.PI * 2);
                    this.ctx.fill();
                });
            }

            draw() {
                // 清空画布
                this.ctx.fillStyle = 'rgba(15, 23, 42, 0.3)';
                this.ctx.fillRect(0, 0, this.width, this.height);

                // 绘制原子核
                this.ctx.fillStyle = COLORS.accent;
                this.ctx.beginPath();
                this.ctx.arc(this.width / 2, this.height / 2, 5, 0, Math.PI * 2);
                this.ctx.fill();

                // 绘制电子云
                this.drawOrbital();

                // 绘制坐标轴
                if (this.showAxes) {
                    this.drawAxes();
                }
            }

            animate() {
                if (!this.isDragging && this.rotationSpeed > 0) {
                    this.rotationY += this.rotationSpeed * 0.01;
                }

                if (this.animateElectrons) {
                    this.time += 0.05;
                }

                this.draw();
                requestAnimationFrame(() => this.animate());
            }
        }

        // 初始化
        const simulator = new OrbitalSimulator();
        simulator.updateTransitionInfo();
    </script>
</body>
</html>$HTML$,
 75,
 21,
 1057,
 false,
 0,
 NOW(),
 '{"name": "电子轨道", "description": "原子电子轨道的3D可视化，展示不同能级的轨道形状", "difficulty": "hard", "render_mode": "html"}');


-- [8/24] 分子结构 (chemistry, 75分)
INSERT INTO simulator_templates
(subject, topic, code, quality_score, visual_elements, line_count, has_setup_update, variable_count, created_at, metadata)
VALUES
('chemistry',
 '分子结构',
 $HTML$<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>分子结构 - 化学交互模拟器</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
            color: #F1F5F9;
            min-height: 100vh;
            padding: 20px;
            overflow-x: hidden;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        header {
            text-align: center;
            margin-bottom: 30px;
            animation: fadeInDown 0.6s ease-out;
        }

        h1 {
            font-size: 2.5em;
            color: #DC2626;
            margin-bottom: 10px;
            text-shadow: 0 2px 10px rgba(220, 38, 38, 0.3);
        }

        .subtitle {
            font-size: 1.1em;
            color: #94A3B8;
        }

        .main-content {
            display: grid;
            grid-template-columns: 300px 1fr;
            gap: 20px;
            animation: fadeIn 0.8s ease-out;
        }

        .control-panel {
            background: rgba(30, 41, 59, 0.8);
            border: 2px solid rgba(220, 38, 38, 0.3);
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(10px);
            height: fit-content;
        }

        .panel-section {
            margin-bottom: 25px;
        }

        .panel-section h3 {
            color: #DC2626;
            font-size: 1.2em;
            margin-bottom: 15px;
            border-bottom: 2px solid rgba(220, 38, 38, 0.3);
            padding-bottom: 8px;
        }

        .molecule-selector {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 15px;
        }

        .molecule-btn {
            background: linear-gradient(135deg, rgba(220, 38, 38, 0.2), rgba(220, 38, 38, 0.1));
            border: 2px solid rgba(220, 38, 38, 0.3);
            color: #F1F5F9;
            padding: 12px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 0.95em;
            font-weight: 500;
        }

        .molecule-btn:hover {
            background: linear-gradient(135deg, rgba(220, 38, 38, 0.4), rgba(220, 38, 38, 0.2));
            border-color: #DC2626;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(220, 38, 38, 0.3);
        }

        .molecule-btn.active {
            background: linear-gradient(135deg, #DC2626, #B91C1C);
            border-color: #DC2626;
            box-shadow: 0 5px 20px rgba(220, 38, 38, 0.4);
        }

        .slider-group {
            margin-bottom: 20px;
        }

        .slider-label {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 0.95em;
            color: #CBD5E1;
        }

        .slider-value {
            color: #DC2626;
            font-weight: 600;
        }

        input[type="range"] {
            width: 100%;
            height: 6px;
            border-radius: 3px;
            background: linear-gradient(90deg, rgba(220, 38, 38, 0.3), rgba(220, 38, 38, 0.6));
            outline: none;
            -webkit-appearance: none;
        }

        input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: #DC2626;
            cursor: pointer;
            box-shadow: 0 2px 8px rgba(220, 38, 38, 0.4);
            transition: all 0.3s ease;
        }

        input[type="range"]::-webkit-slider-thumb:hover {
            transform: scale(1.2);
            box-shadow: 0 3px 12px rgba(220, 38, 38, 0.6);
        }

        .checkbox-group {
            display: flex;
            align-items: center;
            margin-bottom: 12px;
            cursor: pointer;
        }

        .checkbox-group input[type="checkbox"] {
            width: 20px;
            height: 20px;
            margin-right: 10px;
            cursor: pointer;
            accent-color: #DC2626;
        }

        .info-box {
            background: rgba(37, 99, 235, 0.1);
            border: 2px solid rgba(37, 99, 235, 0.3);
            border-radius: 10px;
            padding: 15px;
            margin-top: 20px;
        }

        .info-box h4 {
            color: #2563EB;
            margin-bottom: 10px;
            font-size: 1.05em;
        }

        .info-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 0.9em;
        }

        .info-label {
            color: #94A3B8;
        }

        .info-value {
            color: #10B981;
            font-weight: 600;
        }

        .canvas-container {
            background: rgba(15, 23, 42, 0.6);
            border: 2px solid rgba(220, 38, 38, 0.3);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            position: relative;
        }

        #moleculeCanvas {
            width: 100%;
            height: 700px;
            border-radius: 10px;
            background: radial-gradient(circle at center, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.9));
            cursor: grab;
        }

        #moleculeCanvas:active {
            cursor: grabbing;
        }

        .legend {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 15px;
            flex-wrap: wrap;
        }

        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.95em;
        }

        .legend-color {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            border: 2px solid rgba(255, 255, 255, 0.3);
        }

        .instructions {
            position: absolute;
            top: 30px;
            right: 30px;
            background: rgba(30, 41, 59, 0.9);
            border: 2px solid rgba(220, 38, 38, 0.3);
            border-radius: 10px;
            padding: 15px;
            font-size: 0.9em;
            max-width: 250px;
            backdrop-filter: blur(10px);
        }

        .instructions h4 {
            color: #DC2626;
            margin-bottom: 10px;
        }

        .instructions ul {
            list-style: none;
            padding-left: 0;
        }

        .instructions li {
            margin-bottom: 6px;
            color: #CBD5E1;
            padding-left: 20px;
            position: relative;
        }

        .instructions li::before {
            content: "▸";
            position: absolute;
            left: 0;
            color: #DC2626;
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes pulse {
            0%, 100% {
                transform: scale(1);
            }
            50% {
                transform: scale(1.05);
            }
        }

        @media (max-width: 1024px) {
            .main-content {
                grid-template-columns: 1fr;
            }

            .control-panel {
                order: 2;
            }

            .instructions {
                position: static;
                margin-bottom: 15px;
                max-width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔬 分子结构三维模拟器</h1>
            <p class="subtitle">探索化学键与分子几何结构</p>
        </header>

        <div class="main-content">
            <aside class="control-panel">
                <div class="panel-section">
                    <h3>选择分子</h3>
                    <div class="molecule-selector">
                        <button class="molecule-btn active" data-molecule="H2O">H₂O</button>
                        <button class="molecule-btn" data-molecule="CO2">CO₂</button>
                        <button class="molecule-btn" data-molecule="CH4">CH₄</button>
                        <button class="molecule-btn" data-molecule="NH3">NH₃</button>
                        <button class="molecule-btn" data-molecule="C2H6">C₂H₆</button>
                        <button class="molecule-btn" data-molecule="O2">O₂</button>
                    </div>
                </div>

                <div class="panel-section">
                    <h3>视图控制</h3>
                    <div class="slider-group">
                        <div class="slider-label">
                            <span>旋转速度</span>
                            <span class="slider-value" id="rotationValue">0.5°/帧</span>
                        </div>
                        <input type="range" id="rotationSpeed" min="0" max="3" step="0.1" value="0.5">
                    </div>

                    <div class="slider-group">
                        <div class="slider-label">
                            <span>缩放比例</span>
                            <span class="slider-value" id="zoomValue">100%</span>
                        </div>
                        <input type="range" id="zoomLevel" min="50" max="200" step="5" value="100">
                    </div>

                    <div class="slider-group">
                        <div class="slider-label">
                            <span>原子半径</span>
                            <span class="slider-value" id="atomSizeValue">1.0x</span>
                        </div>
                        <input type="range" id="atomSize" min="0.5" max="2" step="0.1" value="1">
                    </div>
                </div>

                <div class="panel-section">
                    <h3>显示选项</h3>
                    <label class="checkbox-group">
                        <input type="checkbox" id="showBonds" checked>
                        <span>显示化学键</span>
                    </label>
                    <label class="checkbox-group">
                        <input type="checkbox" id="showLabels" checked>
                        <span>显示原子标签</span>
                    </label>
                    <label class="checkbox-group">
                        <input type="checkbox" id="showAngles">
                        <span>显示键角</span>
                    </label>
                    <label class="checkbox-group">
                        <input type="checkbox" id="showDistances">
                        <span>显示键长</span>
                    </label>
                </div>

                <div class="info-box">
                    <h4>分子信息</h4>
                    <div class="info-item">
                        <span class="info-label">分子式:</span>
                        <span class="info-value" id="infoFormula">H₂O</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">几何构型:</span>
                        <span class="info-value" id="infoGeometry">V形</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">键类型:</span>
                        <span class="info-value" id="infoBondType">共价键</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">键角:</span>
                        <span class="info-value" id="infoAngle">104.5°</span>
                    </div>
                </div>
            </aside>

            <main class="canvas-container">
                <div class="instructions">
                    <h4>操作说明</h4>
                    <ul>
                        <li>拖动鼠标旋转分子</li>
                        <li>滚轮缩放视图</li>
                        <li>点击原子查看详情</li>
                        <li>双击重置视角</li>
                    </ul>
                </div>
                <canvas id="moleculeCanvas"></canvas>
                <div class="legend">
                    <div class="legend-item">
                        <div class="legend-color" style="background: #FF4444;"></div>
                        <span>氧 (O)</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #FFFFFF;"></div>
                        <span>氢 (H)</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #888888;"></div>
                        <span>碳 (C)</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #4444FF;"></div>
                        <span>氮 (N)</span>
                    </div>
                </div>
            </main>
        </div>
    </div>

    <script>
        const COLORS = {
            primary: '#DC2626',
            secondary: '#2563EB',
            accent: '#10B981',
            background: '#1E293B',
            text: '#F1F5F9'
        };

        const ATOM_COLORS = {
            'H': '#FFFFFF',
            'O': '#FF4444',
            'C': '#888888',
            'N': '#4444FF'
        };

        const MOLECULES = {
            'H2O': {
                name: '水',
                formula: 'H₂O',
                geometry: 'V形',
                bondType: '共价键',
                angle: '104.5°',
                atoms: [
                    { element: 'O', x: 0, y: 0, z: 0 },
                    { element: 'H', x: 0.96, y: 0, z: 0 },
                    { element: 'H', x: -0.24, y: 0.93, z: 0 }
                ],
                bonds: [[0, 1], [0, 2]]
            },
            'CO2': {
                name: '二氧化碳',
                formula: 'CO₂',
                geometry: '直线形',
                bondType: '共价键',
                angle: '180°',
                atoms: [
                    { element: 'C', x: 0, y: 0, z: 0 },
                    { element: 'O', x: -1.16, y: 0, z: 0 },
                    { element: 'O', x: 1.16, y: 0, z: 0 }
                ],
                bonds: [[0, 1], [0, 2]]
            },
            'CH4': {
                name: '甲烷',
                formula: 'CH₄',
                geometry: '正四面体',
                bondType: '共价键',
                angle: '109.5°',
                atoms: [
                    { element: 'C', x: 0, y: 0, z: 0 },
                    { element: 'H', x: 0.63, y: 0.63, z: 0.63 },
                    { element: 'H', x: -0.63, y: -0.63, z: 0.63 },
                    { element: 'H', x: -0.63, y: 0.63, z: -0.63 },
                    { element: 'H', x: 0.63, y: -0.63, z: -0.63 }
                ],
                bonds: [[0, 1], [0, 2], [0, 3], [0, 4]]
            },
            'NH3': {
                name: '氨',
                formula: 'NH₃',
                geometry: '三角锥形',
                bondType: '共价键',
                angle: '107°',
                atoms: [
                    { element: 'N', x: 0, y: 0, z: 0 },
                    { element: 'H', x: 0.94, y: 0, z: 0 },
                    { element: 'H', x: -0.47, y: 0.81, z: 0 },
                    { element: 'H', x: -0.47, y: -0.41, z: 0.7 }
                ],
                bonds: [[0, 1], [0, 2], [0, 3]]
            },
            'C2H6': {
                name: '乙烷',
                formula: 'C₂H₆',
                geometry: '交错构象',
                bondType: '共价键',
                angle: '109.5°',
                atoms: [
                    { element: 'C', x: -0.75, y: 0, z: 0 },
                    { element: 'C', x: 0.75, y: 0, z: 0 },
                    { element: 'H', x: -1.15, y: 0.95, z: 0 },
                    { element: 'H', x: -1.15, y: -0.48, z: 0.82 },
                    { element: 'H', x: -1.15, y: -0.48, z: -0.82 },
                    { element: 'H', x: 1.15, y: 0.95, z: 0 },
                    { element: 'H', x: 1.15, y: -0.48, z: 0.82 },
                    { element: 'H', x: 1.15, y: -0.48, z: -0.82 }
                ],
                bonds: [[0, 1], [0, 2], [0, 3], [0, 4], [1, 5], [1, 6], [1, 7]]
            },
            'O2': {
                name: '氧气',
                formula: 'O₂',
                geometry: '直线形',
                bondType: '双键',
                angle: '180°',
                atoms: [
                    { element: 'O', x: -0.6, y: 0, z: 0 },
                    { element: 'O', x: 0.6, y: 0, z: 0 }
                ],
                bonds: [[0, 1]]
            }
        };

        class MoleculeSimulator {
            constructor() {
                this.canvas = document.getElementById('moleculeCanvas');
                this.ctx = this.canvas.getContext('2d');
                this.setupCanvas();

                this.currentMolecule = 'H2O';
                this.rotationX = 0.3;
                this.rotationY = 0.3;
                this.rotationSpeed = 0.5;
                this.zoomLevel = 1.0;
                this.atomSizeMultiplier = 1.0;

                this.showBonds = true;
                this.showLabels = true;
                this.showAngles = false;
                this.showDistances = false;

                this.isDragging = false;
                this.lastMouseX = 0;
                this.lastMouseY = 0;

                this.setupEventListeners();
                this.animate();
            }

            setupCanvas() {
                const rect = this.canvas.getBoundingClientRect();
                this.canvas.width = rect.width * window.devicePixelRatio;
                this.canvas.height = rect.height * window.devicePixelRatio;
                this.ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
                this.width = rect.width;
                this.height = rect.height;
            }

            setupEventListeners() {
                // 分子选择
                document.querySelectorAll('.molecule-btn').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        document.querySelectorAll('.molecule-btn').forEach(b => b.classList.remove('active'));
                        e.target.classList.add('active');
                        this.currentMolecule = e.target.dataset.molecule;
                        this.updateInfo();
                    });
                });

                // 滑块控制
                document.getElementById('rotationSpeed').addEventListener('input', (e) => {
                    this.rotationSpeed = parseFloat(e.target.value);
                    document.getElementById('rotationValue').textContent = `${this.rotationSpeed.toFixed(1)}°/帧`;
                });

                document.getElementById('zoomLevel').addEventListener('input', (e) => {
                    this.zoomLevel = parseFloat(e.target.value) / 100;
                    document.getElementById('zoomValue').textContent = `${e.target.value}%`;
                });

                document.getElementById('atomSize').addEventListener('input', (e) => {
                    this.atomSizeMultiplier = parseFloat(e.target.value);
                    document.getElementById('atomSizeValue').textContent = `${e.target.value}x`;
                });

                // 复选框
                document.getElementById('showBonds').addEventListener('change', (e) => {
                    this.showBonds = e.target.checked;
                });

                document.getElementById('showLabels').addEventListener('change', (e) => {
                    this.showLabels = e.target.checked;
                });

                document.getElementById('showAngles').addEventListener('change', (e) => {
                    this.showAngles = e.target.checked;
                });

                document.getElementById('showDistances').addEventListener('change', (e) => {
                    this.showDistances = e.target.checked;
                });

                // 鼠标拖动
                this.canvas.addEventListener('mousedown', (e) => {
                    this.isDragging = true;
                    this.lastMouseX = e.clientX;
                    this.lastMouseY = e.clientY;
                });

                this.canvas.addEventListener('mousemove', (e) => {
                    if (this.isDragging) {
                        const deltaX = e.clientX - this.lastMouseX;
                        const deltaY = e.clientY - this.lastMouseY;
                        this.rotationY += deltaX * 0.01;
                        this.rotationX += deltaY * 0.01;
                        this.lastMouseX = e.clientX;
                        this.lastMouseY = e.clientY;
                    }
                });

                this.canvas.addEventListener('mouseup', () => {
                    this.isDragging = false;
                });

                this.canvas.addEventListener('mouseleave', () => {
                    this.isDragging = false;
                });

                // 鼠标滚轮缩放
                this.canvas.addEventListener('wheel', (e) => {
                    e.preventDefault();
                    const delta = e.deltaY > 0 ? 0.95 : 1.05;
                    this.zoomLevel = Math.max(0.5, Math.min(2, this.zoomLevel * delta));
                    document.getElementById('zoomLevel').value = this.zoomLevel * 100;
                    document.getElementById('zoomValue').textContent = `${Math.round(this.zoomLevel * 100)}%`;
                });

                // 双击重置
                this.canvas.addEventListener('dblclick', () => {
                    this.rotationX = 0.3;
                    this.rotationY = 0.3;
                    this.zoomLevel = 1.0;
                    document.getElementById('zoomLevel').value = 100;
                    document.getElementById('zoomValue').textContent = '100%';
                });

                window.addEventListener('resize', () => {
                    this.setupCanvas();
                });
            }

            updateInfo() {
                const mol = MOLECULES[this.currentMolecule];
                document.getElementById('infoFormula').textContent = mol.formula;
                document.getElementById('infoGeometry').textContent = mol.geometry;
                document.getElementById('infoBondType').textContent = mol.bondType;
                document.getElementById('infoAngle').textContent = mol.angle;
            }

            project3D(x, y, z) {
                // 旋转
                let cosX = Math.cos(this.rotationX);
                let sinX = Math.sin(this.rotationX);
                let cosY = Math.cos(this.rotationY);
                let sinY = Math.sin(this.rotationY);

                let y1 = y * cosX - z * sinX;
                let z1 = y * sinX + z * cosX;

                let x2 = x * cosY + z1 * sinY;
                let z2 = -x * sinY + z1 * cosY;

                // 透视投影
                const scale = 150 * this.zoomLevel;
                const perspective = 600;
                const factor = perspective / (perspective + z2);

                return {
                    x: this.width / 2 + x2 * scale * factor,
                    y: this.height / 2 + y1 * scale * factor,
                    z: z2,
                    scale: factor
                };
            }

            drawAtom(atom, projected, baseRadius) {
                const radius = baseRadius * projected.scale * this.atomSizeMultiplier;
                const color = ATOM_COLORS[atom.element];

                // 外发光
                const gradient = this.ctx.createRadialGradient(
                    projected.x, projected.y, 0,
                    projected.x, projected.y, radius * 1.5
                );
                gradient.addColorStop(0, color);
                gradient.addColorStop(0.7, color);
                gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');

                this.ctx.beginPath();
                this.ctx.arc(projected.x, projected.y, radius * 1.5, 0, Math.PI * 2);
                this.ctx.fillStyle = gradient;
                this.ctx.fill();

                // 主体
                this.ctx.beginPath();
                this.ctx.arc(projected.x, projected.y, radius, 0, Math.PI * 2);
                this.ctx.fillStyle = color;
                this.ctx.fill();

                // 高光
                const highlight = this.ctx.createRadialGradient(
                    projected.x - radius * 0.3, projected.y - radius * 0.3, 0,
                    projected.x - radius * 0.3, projected.y - radius * 0.3, radius * 0.8
                );
                highlight.addColorStop(0, 'rgba(255, 255, 255, 0.6)');
                highlight.addColorStop(1, 'rgba(255, 255, 255, 0)');

                this.ctx.beginPath();
                this.ctx.arc(projected.x, projected.y, radius, 0, Math.PI * 2);
                this.ctx.fillStyle = highlight;
                this.ctx.fill();

                // 边框
                this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
                this.ctx.lineWidth = 2;
                this.ctx.stroke();

                // 标签
                if (this.showLabels) {
                    this.ctx.fillStyle = COLORS.text;
                    this.ctx.font = 'bold 16px Arial';
                    this.ctx.textAlign = 'center';
                    this.ctx.textBaseline = 'middle';
                    this.ctx.fillText(atom.element, projected.x, projected.y);
                }
            }

            drawBond(proj1, proj2, isDouble = false) {
                this.ctx.strokeStyle = 'rgba(16, 185, 129, 0.8)';
                this.ctx.lineWidth = 4;
                this.ctx.lineCap = 'round';

                if (isDouble) {
                    // 双键
                    const dx = proj2.x - proj1.x;
                    const dy = proj2.y - proj1.y;
                    const len = Math.sqrt(dx * dx + dy * dy);
                    const offsetX = -dy / len * 5;
                    const offsetY = dx / len * 5;

                    this.ctx.beginPath();
                    this.ctx.moveTo(proj1.x + offsetX, proj1.y + offsetY);
                    this.ctx.lineTo(proj2.x + offsetX, proj2.y + offsetY);
                    this.ctx.stroke();

                    this.ctx.beginPath();
                    this.ctx.moveTo(proj1.x - offsetX, proj1.y - offsetY);
                    this.ctx.lineTo(proj2.x - offsetX, proj2.y - offsetY);
                    this.ctx.stroke();
                } else {
                    this.ctx.beginPath();
                    this.ctx.moveTo(proj1.x, proj1.y);
                    this.ctx.lineTo(proj2.x, proj2.y);
                    this.ctx.stroke();
                }

                // 显示键长
                if (this.showDistances) {
                    const midX = (proj1.x + proj2.x) / 2;
                    const midY = (proj1.y + proj2.y) / 2;
                    const dx = proj2.x - proj1.x;
                    const dy = proj2.y - proj1.y;
                    const distance = Math.sqrt(dx * dx + dy * dy) / (150 * this.zoomLevel);

                    this.ctx.fillStyle = COLORS.secondary;
                    this.ctx.font = '12px Arial';
                    this.ctx.textAlign = 'center';
                    this.ctx.fillText(`${distance.toFixed(2)}Å`, midX, midY - 10);
                }
            }

            draw() {
                // 清空画布
                this.ctx.fillStyle = 'rgba(15, 23, 42, 0.3)';
                this.ctx.fillRect(0, 0, this.width, this.height);

                const mol = MOLECULES[this.currentMolecule];

                // 投影所有原子
                const projected = mol.atoms.map(atom => ({
                    atom,
                    proj: this.project3D(atom.x, atom.y, atom.z)
                }));

                // 按Z轴深度排序
                projected.sort((a, b) => a.proj.z - b.proj.z);

                // 绘制化学键
                if (this.showBonds) {
                    mol.bonds.forEach(([i, j]) => {
                        const proj1 = this.project3D(mol.atoms[i].x, mol.atoms[i].y, mol.atoms[i].z);
                        const proj2 = this.project3D(mol.atoms[j].x, mol.atoms[j].y, mol.atoms[j].z);
                        const isDouble = this.currentMolecule === 'O2';
                        this.drawBond(proj1, proj2, isDouble);
                    });
                }

                // 绘制键角
                if (this.showAngles && mol.bonds.length >= 2) {
                    const center = mol.atoms[0];
                    const centerProj = this.project3D(center.x, center.y, center.z);

                    this.ctx.strokeStyle = COLORS.primary;
                    this.ctx.lineWidth = 2;
                    this.ctx.setLineDash([5, 5]);
                    this.ctx.beginPath();
                    this.ctx.arc(centerProj.x, centerProj.y, 40, 0, Math.PI * 2);
                    this.ctx.stroke();
                    this.ctx.setLineDash([]);

                    this.ctx.fillStyle = COLORS.primary;
                    this.ctx.font = 'bold 14px Arial';
                    this.ctx.textAlign = 'center';
                    this.ctx.fillText(mol.angle, centerProj.x, centerProj.y + 60);
                }

                // 绘制原子
                projected.forEach(({ atom, proj }) => {
                    this.drawAtom(atom, proj, 30);
                });
            }

            animate() {
                if (!this.isDragging && this.rotationSpeed > 0) {
                    this.rotationY += this.rotationSpeed * 0.01;
                }

                this.draw();
                requestAnimationFrame(() => this.animate());
            }
        }

        // 初始化
        const simulator = new MoleculeSimulator();
        simulator.updateInfo();
    </script>
</body>
</html>$HTML$,
 75,
 55,
 871,
 false,
 0,
 NOW(),
 '{"name": "分子结构", "description": "分子的3D结构展示和旋转", "difficulty": "medium", "render_mode": "html"}');


-- [9/24] 化学平衡 (chemistry, 75分)
INSERT INTO simulator_templates
(subject, topic, code, quality_score, visual_elements, line_count, has_setup_update, variable_count, created_at, metadata)
VALUES
('chemistry',
 '化学平衡',
 $HTML$<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>化学平衡 - 化学交互模拟器</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
            color: #F1F5F9;
            min-height: 100vh;
            padding: 20px;
            overflow-x: hidden;
        }

        .container {
            max-width: 1600px;
            margin: 0 auto;
        }

        header {
            text-align: center;
            margin-bottom: 30px;
            animation: fadeInDown 0.6s ease-out;
        }

        h1 {
            font-size: 2.5em;
            color: #DC2626;
            margin-bottom: 10px;
            text-shadow: 0 2px 10px rgba(220, 38, 38, 0.3);
        }

        .subtitle {
            font-size: 1.1em;
            color: #94A3B8;
        }

        .main-grid {
            display: grid;
            grid-template-columns: 300px 1fr;
            gap: 20px;
            animation: fadeIn 0.8s ease-out;
        }

        .control-panel {
            background: rgba(30, 41, 59, 0.8);
            border: 2px solid rgba(220, 38, 38, 0.3);
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(10px);
            height: fit-content;
        }

        .panel-section {
            margin-bottom: 25px;
        }

        .panel-section h3 {
            color: #DC2626;
            font-size: 1.2em;
            margin-bottom: 15px;
            border-bottom: 2px solid rgba(220, 38, 38, 0.3);
            padding-bottom: 8px;
        }

        .slider-group {
            margin-bottom: 20px;
        }

        .slider-label {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 0.95em;
            color: #CBD5E1;
        }

        .slider-value {
            color: #DC2626;
            font-weight: 600;
        }

        input[type="range"] {
            width: 100%;
            height: 6px;
            border-radius: 3px;
            background: linear-gradient(90deg, rgba(220, 38, 38, 0.3), rgba(220, 38, 38, 0.6));
            outline: none;
            -webkit-appearance: none;
        }

        input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: #DC2626;
            cursor: pointer;
            box-shadow: 0 2px 8px rgba(220, 38, 38, 0.4);
            transition: all 0.3s ease;
        }

        input[type="range"]::-webkit-slider-thumb:hover {
            transform: scale(1.2);
            box-shadow: 0 3px 12px rgba(220, 38, 38, 0.6);
        }

        .button-group {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 15px;
        }

        .control-btn {
            background: linear-gradient(135deg, rgba(220, 38, 38, 0.2), rgba(220, 38, 38, 0.1));
            border: 2px solid rgba(220, 38, 38, 0.3);
            color: #F1F5F9;
            padding: 12px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 0.95em;
            font-weight: 500;
        }

        .control-btn:hover {
            background: linear-gradient(135deg, rgba(220, 38, 38, 0.4), rgba(220, 38, 38, 0.2));
            border-color: #DC2626;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(220, 38, 38, 0.3);
        }

        .control-btn.active {
            background: linear-gradient(135deg, #DC2626, #B91C1C);
            border-color: #DC2626;
            box-shadow: 0 5px 20px rgba(220, 38, 38, 0.4);
        }

        .checkbox-group {
            display: flex;
            align-items: center;
            margin-bottom: 12px;
            cursor: pointer;
        }

        .checkbox-group input[type="checkbox"] {
            width: 20px;
            height: 20px;
            margin-right: 10px;
            cursor: pointer;
            accent-color: #DC2626;
        }

        .stats-box {
            background: rgba(37, 99, 235, 0.1);
            border: 2px solid rgba(37, 99, 235, 0.3);
            border-radius: 10px;
            padding: 15px;
            margin-top: 20px;
        }

        .stats-box h4 {
            color: #2563EB;
            margin-bottom: 10px;
            font-size: 1.05em;
        }

        .stat-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 0.9em;
        }

        .stat-label {
            color: #94A3B8;
        }

        .stat-value {
            color: #10B981;
            font-weight: 600;
        }

        .content-grid {
            display: grid;
            grid-template-rows: 400px 1fr;
            gap: 20px;
        }

        .visualization-container {
            background: rgba(15, 23, 42, 0.6);
            border: 2px solid rgba(220, 38, 38, 0.3);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            position: relative;
        }

        #reactionCanvas {
            width: 100%;
            height: 100%;
            border-radius: 10px;
            background: radial-gradient(circle at center, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.9));
        }

        .chart-container {
            background: rgba(15, 23, 42, 0.6);
            border: 2px solid rgba(220, 38, 38, 0.3);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
        }

        .chart-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }

        .chart-header h3 {
            color: #DC2626;
            font-size: 1.3em;
        }

        #concentrationChart {
            width: 100%;
            height: calc(100% - 50px);
            border-radius: 10px;
            background: rgba(30, 41, 59, 0.4);
        }

        .legend {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 15px;
            flex-wrap: wrap;
        }

        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.95em;
        }

        .legend-line {
            width: 30px;
            height: 3px;
            border-radius: 2px;
        }

        .equation-display {
            position: absolute;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(30, 41, 59, 0.95);
            border: 2px solid rgba(220, 38, 38, 0.4);
            border-radius: 10px;
            padding: 15px 30px;
            font-size: 1.5em;
            font-weight: bold;
            color: #F1F5F9;
            backdrop-filter: blur(10px);
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);
        }

        .equilibrium-arrow {
            color: #10B981;
            margin: 0 15px;
            animation: pulse 2s ease-in-out infinite;
        }

        .molecule-label {
            color: #DC2626;
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes pulse {
            0%, 100% {
                transform: scale(1);
            }
            50% {
                transform: scale(1.1);
            }
        }

        @media (max-width: 1024px) {
            .main-grid {
                grid-template-columns: 1fr;
            }

            .content-grid {
                grid-template-rows: 350px 400px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>⚖️ 化学平衡模拟器</h1>
            <p class="subtitle">探索可逆反应与勒夏特列原理</p>
        </header>

        <div class="main-grid">
            <aside class="control-panel">
                <div class="panel-section">
                    <h3>反应控制</h3>
                    <div class="button-group">
                        <button class="control-btn active" id="startBtn">开始反应</button>
                        <button class="control-btn" id="pauseBtn">暂停</button>
                        <button class="control-btn" id="resetBtn">重置</button>
                        <button class="control-btn" id="equilibriumBtn">快速平衡</button>
                    </div>
                </div>

                <div class="panel-section">
                    <h3>初始条件</h3>
                    <div class="slider-group">
                        <div class="slider-label">
                            <span>[A] 初始浓度</span>
                            <span class="slider-value" id="concAValue">2.0 M</span>
                        </div>
                        <input type="range" id="concA" min="0" max="5" step="0.1" value="2">
                    </div>

                    <div class="slider-group">
                        <div class="slider-label">
                            <span>[B] 初始浓度</span>
                            <span class="slider-value" id="concBValue">0.5 M</span>
                        </div>
                        <input type="range" id="concB" min="0" max="5" step="0.1" value="0.5">
                    </div>
                </div>

                <div class="panel-section">
                    <h3>反应参数</h3>
                    <div class="slider-group">
                        <div class="slider-label">
                            <span>温度</span>
                            <span class="slider-value" id="tempValue">298 K</span>
                        </div>
                        <input type="range" id="temperature" min="273" max="373" step="5" value="298">
                    </div>

                    <div class="slider-group">
                        <div class="slider-label">
                            <span>正反应速率常数 k₁</span>
                            <span class="slider-value" id="k1Value">0.05</span>
                        </div>
                        <input type="range" id="k1" min="0.01" max="0.2" step="0.01" value="0.05">
                    </div>

                    <div class="slider-group">
                        <div class="slider-label">
                            <span>逆反应速率常数 k₂</span>
                            <span class="slider-value" id="k2Value">0.03</span>
                        </div>
                        <input type="range" id="k2" min="0.01" max="0.2" step="0.01" value="0.03">
                    </div>
                </div>

                <div class="panel-section">
                    <h3>显示选项</h3>
                    <label class="checkbox-group">
                        <input type="checkbox" id="showParticles" checked>
                        <span>显示粒子动画</span>
                    </label>
                    <label class="checkbox-group">
                        <input type="checkbox" id="showGrid" checked>
                        <span>显示网格</span>
                    </label>
                    <label class="checkbox-group">
                        <input type="checkbox" id="showEquilibriumLine" checked>
                        <span>显示平衡线</span>
                    </label>
                </div>

                <div class="stats-box">
                    <h4>实时数据</h4>
                    <div class="stat-item">
                        <span class="stat-label">时间:</span>
                        <span class="stat-value" id="timeValue">0.0 s</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">[A] 浓度:</span>
                        <span class="stat-value" id="currentConcA">2.00 M</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">[B] 浓度:</span>
                        <span class="stat-value" id="currentConcB">0.50 M</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">平衡常数 Kc:</span>
                        <span class="stat-value" id="kcValue">1.67</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">反应商 Q:</span>
                        <span class="stat-value" id="qValue">0.25</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">状态:</span>
                        <span class="stat-value" id="statusValue">正向进行</span>
                    </div>
                </div>
            </aside>

            <div class="content-grid">
                <div class="visualization-container">
                    <div class="equation-display">
                        <span class="molecule-label">A</span>
                        <span class="equilibrium-arrow">⇌</span>
                        <span class="molecule-label">B</span>
                    </div>
                    <canvas id="reactionCanvas"></canvas>
                </div>

                <div class="chart-container">
                    <div class="chart-header">
                        <h3>浓度-时间曲线</h3>
                        <div class="legend">
                            <div class="legend-item">
                                <div class="legend-line" style="background: #DC2626;"></div>
                                <span>反应物 [A]</span>
                            </div>
                            <div class="legend-item">
                                <div class="legend-line" style="background: #2563EB;"></div>
                                <span>生成物 [B]</span>
                            </div>
                        </div>
                    </div>
                    <canvas id="concentrationChart"></canvas>
                </div>
            </div>
        </div>
    </div>

    <script>
        const COLORS = {
            primary: '#DC2626',
            secondary: '#2563EB',
            accent: '#10B981',
            background: '#1E293B',
            text: '#F1F5F9'
        };

        class Particle {
            constructor(x, y, type, canvas) {
                this.x = x;
                this.y = y;
                this.type = type; // 'A' or 'B'
                this.vx = (Math.random() - 0.5) * 3;
                this.vy = (Math.random() - 0.5) * 3;
                this.radius = 8;
                this.canvas = canvas;
            }

            update() {
                this.x += this.vx;
                this.y += this.vy;

                // 边界反弹
                if (this.x < this.radius || this.x > this.canvas.width - this.radius) {
                    this.vx *= -1;
                    this.x = Math.max(this.radius, Math.min(this.canvas.width - this.radius, this.x));
                }
                if (this.y < this.radius || this.y > this.canvas.height - this.radius) {
                    this.vy *= -1;
                    this.y = Math.max(this.radius, Math.min(this.canvas.height - this.radius, this.y));
                }
            }

            draw(ctx) {
                const color = this.type === 'A' ? COLORS.primary : COLORS.secondary;

                // 外发光
                const gradient = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, this.radius * 2);
                gradient.addColorStop(0, color);
                gradient.addColorStop(0.5, color + '80');
                gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');

                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius * 2, 0, Math.PI * 2);
                ctx.fillStyle = gradient;
                ctx.fill();

                // 主体
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                ctx.fillStyle = color;
                ctx.fill();

                // 标签
                ctx.fillStyle = COLORS.text;
                ctx.font = 'bold 10px Arial';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(this.type, this.x, this.y);
            }
        }

        class EquilibriumSimulator {
            constructor() {
                this.reactionCanvas = document.getElementById('reactionCanvas');
                this.reactionCtx = this.reactionCanvas.getContext('2d');
                this.chartCanvas = document.getElementById('concentrationChart');
                this.chartCtx = this.chartCanvas.getContext('2d');

                this.setupCanvases();

                // 反应参数
                this.concA = 2.0;
                this.concB = 0.5;
                this.initialConcA = 2.0;
                this.initialConcB = 0.5;
                this.k1 = 0.05; // 正反应速率常数
                this.k2 = 0.03; // 逆反应速率常数
                this.temperature = 298;

                // 模拟状态
                this.time = 0;
                this.isRunning = false;
                this.showParticles = true;
                this.showGrid = true;
                this.showEquilibriumLine = true;

                // 粒子系统
                this.particles = [];
                this.initializeParticles();

                // 数据记录
                this.dataPoints = [];
                this.maxDataPoints = 500;

                this.setupEventListeners();
                this.animate();
            }

            setupCanvases() {
                const reactionRect = this.reactionCanvas.getBoundingClientRect();
                this.reactionCanvas.width = reactionRect.width;
                this.reactionCanvas.height = reactionRect.height;

                const chartRect = this.chartCanvas.getBoundingClientRect();
                this.chartCanvas.width = chartRect.width;
                this.chartCanvas.height = chartRect.height;

                window.addEventListener('resize', () => {
                    this.setupCanvases();
                });
            }

            initializeParticles() {
                this.particles = [];
                const totalParticles = 100;
                const ratioA = this.concA / (this.concA + this.concB);
                const numA = Math.round(totalParticles * ratioA);

                for (let i = 0; i < numA; i++) {
                    const x = Math.random() * this.reactionCanvas.width;
                    const y = Math.random() * this.reactionCanvas.height;
                    this.particles.push(new Particle(x, y, 'A', this.reactionCanvas));
                }

                for (let i = numA; i < totalParticles; i++) {
                    const x = Math.random() * this.reactionCanvas.width;
                    const y = Math.random() * this.reactionCanvas.height;
                    this.particles.push(new Particle(x, y, 'B', this.reactionCanvas));
                }
            }

            setupEventListeners() {
                document.getElementById('startBtn').addEventListener('click', () => {
                    this.isRunning = true;
                    document.getElementById('startBtn').classList.add('active');
                    document.getElementById('pauseBtn').classList.remove('active');
                });

                document.getElementById('pauseBtn').addEventListener('click', () => {
                    this.isRunning = false;
                    document.getElementById('pauseBtn').classList.add('active');
                    document.getElementById('startBtn').classList.remove('active');
                });

                document.getElementById('resetBtn').addEventListener('click', () => {
                    this.reset();
                });

                document.getElementById('equilibriumBtn').addEventListener('click', () => {
                    this.jumpToEquilibrium();
                });

                document.getElementById('concA').addEventListener('input', (e) => {
                    this.initialConcA = parseFloat(e.target.value);
                    document.getElementById('concAValue').textContent = `${this.initialConcA.toFixed(1)} M`;
                    if (!this.isRunning) this.reset();
                });

                document.getElementById('concB').addEventListener('input', (e) => {
                    this.initialConcB = parseFloat(e.target.value);
                    document.getElementById('concBValue').textContent = `${this.initialConcB.toFixed(1)} M`;
                    if (!this.isRunning) this.reset();
                });

                document.getElementById('temperature').addEventListener('input', (e) => {
                    this.temperature = parseFloat(e.target.value);
                    document.getElementById('tempValue').textContent = `${this.temperature} K`;
                });

                document.getElementById('k1').addEventListener('input', (e) => {
                    this.k1 = parseFloat(e.target.value);
                    document.getElementById('k1Value').textContent = this.k1.toFixed(3);
                });

                document.getElementById('k2').addEventListener('input', (e) => {
                    this.k2 = parseFloat(e.target.value);
                    document.getElementById('k2Value').textContent = this.k2.toFixed(3);
                });

                document.getElementById('showParticles').addEventListener('change', (e) => {
                    this.showParticles = e.target.checked;
                });

                document.getElementById('showGrid').addEventListener('change', (e) => {
                    this.showGrid = e.target.checked;
                });

                document.getElementById('showEquilibriumLine').addEventListener('change', (e) => {
                    this.showEquilibriumLine = e.target.checked;
                });
            }

            reset() {
                this.time = 0;
                this.concA = this.initialConcA;
                this.concB = this.initialConcB;
                this.dataPoints = [];
                this.initializeParticles();
                this.updateStats();
            }

            jumpToEquilibrium() {
                const Kc = this.k1 / this.k2;
                const total = this.concA + this.concB;
                this.concB = (total * Kc) / (1 + Kc);
                this.concA = total - this.concB;

                const ratioA = this.concA / total;
                this.particles.forEach((p, i) => {
                    p.type = i < this.particles.length * ratioA ? 'A' : 'B';
                });

                this.updateStats();
            }

            updateReaction(dt) {
                if (!this.isRunning) return;

                // A ⇌ B
                const forwardRate = this.k1 * this.concA;
                const reverseRate = this.k2 * this.concB;

                const dConcA = (-forwardRate + reverseRate) * dt;
                this.concA = Math.max(0, this.concA + dConcA);
                this.concB = Math.max(0, this.initialConcA + this.initialConcB - this.concA);

                this.time += dt;

                // 记录数据
                this.dataPoints.push({
                    time: this.time,
                    concA: this.concA,
                    concB: this.concB
                });

                if (this.dataPoints.length > this.maxDataPoints) {
                    this.dataPoints.shift();
                }

                // 更新粒子类型
                if (this.showParticles && Math.random() < 0.1) {
                    const total = this.concA + this.concB;
                    const ratioA = this.concA / total;
                    const targetNumA = Math.round(this.particles.length * ratioA);
                    const currentNumA = this.particles.filter(p => p.type === 'A').length;

                    if (currentNumA > targetNumA) {
                        const particleA = this.particles.find(p => p.type === 'A');
                        if (particleA) particleA.type = 'B';
                    } else if (currentNumA < targetNumA) {
                        const particleB = this.particles.find(p => p.type === 'B');
                        if (particleB) particleB.type = 'A';
                    }
                }

                this.updateStats();
            }

            updateStats() {
                document.getElementById('timeValue').textContent = `${this.time.toFixed(1)} s`;
                document.getElementById('currentConcA').textContent = `${this.concA.toFixed(2)} M`;
                document.getElementById('currentConcB').textContent = `${this.concB.toFixed(2)} M`;

                const Kc = this.k1 / this.k2;
                document.getElementById('kcValue').textContent = Kc.toFixed(2);

                const Q = this.concA > 0 ? this.concB / this.concA : 0;
                document.getElementById('qValue').textContent = Q.toFixed(2);

                let status = '平衡';
                if (Math.abs(Q - Kc) > 0.1) {
                    status = Q < Kc ? '正向进行' : '逆向进行';
                }
                document.getElementById('statusValue').textContent = status;
            }

            drawReactionVisualization() {
                const ctx = this.reactionCtx;
                const w = this.reactionCanvas.width;
                const h = this.reactionCanvas.height;

                // 清空画布
                ctx.fillStyle = 'rgba(15, 23, 42, 0.3)';
                ctx.fillRect(0, 0, w, h);

                // 网格
                if (this.showGrid) {
                    ctx.strokeStyle = 'rgba(220, 38, 38, 0.1)';
                    ctx.lineWidth = 1;
                    const gridSize = 40;
                    for (let x = 0; x < w; x += gridSize) {
                        ctx.beginPath();
                        ctx.moveTo(x, 0);
                        ctx.lineTo(x, h);
                        ctx.stroke();
                    }
                    for (let y = 0; y < h; y += gridSize) {
                        ctx.beginPath();
                        ctx.moveTo(0, y);
                        ctx.lineTo(w, y);
                        ctx.stroke();
                    }
                }

                // 粒子
                if (this.showParticles) {
                    this.particles.forEach(p => {
                        p.update();
                        p.draw(ctx);
                    });
                }

                // 浓度条
                const barHeight = 40;
                const barY = h - 60;
                const barMaxWidth = w - 100;

                const total = this.concA + this.concB;
                const widthA = (this.concA / total) * barMaxWidth;
                const widthB = (this.concB / total) * barMaxWidth;

                // A条
                ctx.fillStyle = COLORS.primary;
                ctx.fillRect(50, barY, widthA, barHeight);
                ctx.fillStyle = COLORS.text;
                ctx.font = 'bold 14px Arial';
                ctx.textAlign = 'left';
                ctx.fillText(`[A]: ${this.concA.toFixed(2)} M`, 50, barY - 5);

                // B条
                ctx.fillStyle = COLORS.secondary;
                ctx.fillRect(50, barY + barHeight + 10, widthB, barHeight);
                ctx.fillStyle = COLORS.text;
                ctx.fillText(`[B]: ${this.concB.toFixed(2)} M`, 50, barY + barHeight + 5);
            }

            drawConcentrationChart() {
                const ctx = this.chartCtx;
                const w = this.chartCanvas.width;
                const h = this.chartCanvas.height;

                // 清空画布
                ctx.fillStyle = 'rgba(30, 41, 59, 0.4)';
                ctx.fillRect(0, 0, w, h);

                if (this.dataPoints.length < 2) return;

                const padding = 50;
                const chartW = w - 2 * padding;
                const chartH = h - 2 * padding;

                // 坐标轴
                ctx.strokeStyle = 'rgba(241, 245, 249, 0.5)';
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.moveTo(padding, padding);
                ctx.lineTo(padding, h - padding);
                ctx.lineTo(w - padding, h - padding);
                ctx.stroke();

                // 找最大值
                const maxTime = this.dataPoints[this.dataPoints.length - 1].time;
                const maxConc = Math.max(this.initialConcA, this.initialConcB) * 1.2;

                // 平衡线
                if (this.showEquilibriumLine) {
                    const Kc = this.k1 / this.k2;
                    const total = this.initialConcA + this.initialConcB;
                    const eqConcB = (total * Kc) / (1 + Kc);
                    const eqY = h - padding - (eqConcB / maxConc) * chartH;

                    ctx.strokeStyle = COLORS.accent;
                    ctx.setLineDash([5, 5]);
                    ctx.lineWidth = 2;
                    ctx.beginPath();
                    ctx.moveTo(padding, eqY);
                    ctx.lineTo(w - padding, eqY);
                    ctx.stroke();
                    ctx.setLineDash([]);

                    ctx.fillStyle = COLORS.accent;
                    ctx.font = '12px Arial';
                    ctx.textAlign = 'right';
                    ctx.fillText('平衡线', w - padding - 5, eqY - 5);
                }

                // 绘制曲线A
                ctx.strokeStyle = COLORS.primary;
                ctx.lineWidth = 3;
                ctx.beginPath();
                this.dataPoints.forEach((point, i) => {
                    const x = padding + (point.time / maxTime) * chartW;
                    const y = h - padding - (point.concA / maxConc) * chartH;
                    if (i === 0) {
                        ctx.moveTo(x, y);
                    } else {
                        ctx.lineTo(x, y);
                    }
                });
                ctx.stroke();

                // 绘制曲线B
                ctx.strokeStyle = COLORS.secondary;
                ctx.lineWidth = 3;
                ctx.beginPath();
                this.dataPoints.forEach((point, i) => {
                    const x = padding + (point.time / maxTime) * chartW;
                    const y = h - padding - (point.concB / maxConc) * chartH;
                    if (i === 0) {
                        ctx.moveTo(x, y);
                    } else {
                        ctx.lineTo(x, y);
                    }
                });
                ctx.stroke();

                // 坐标轴标签
                ctx.fillStyle = COLORS.text;
                ctx.font = '14px Arial';
                ctx.textAlign = 'center';
                ctx.fillText('时间 (s)', w / 2, h - 10);

                ctx.save();
                ctx.translate(15, h / 2);
                ctx.rotate(-Math.PI / 2);
                ctx.fillText('浓度 (M)', 0, 0);
                ctx.restore();

                // 刻度
                ctx.font = '11px Arial';
                ctx.fillStyle = COLORS.text;
                for (let i = 0; i <= 5; i++) {
                    const time = (maxTime / 5) * i;
                    const x = padding + (i / 5) * chartW;
                    ctx.textAlign = 'center';
                    ctx.fillText(time.toFixed(1), x, h - padding + 20);
                }
                for (let i = 0; i <= 5; i++) {
                    const conc = (maxConc / 5) * i;
                    const y = h - padding - (i / 5) * chartH;
                    ctx.textAlign = 'right';
                    ctx.fillText(conc.toFixed(1), padding - 10, y + 4);
                }
            }

            animate() {
                this.updateReaction(0.1);
                this.drawReactionVisualization();
                this.drawConcentrationChart();
                requestAnimationFrame(() => this.animate());
            }
        }

        // 初始化
        const simulator = new EquilibriumSimulator();
    </script>
</body>
</html>$HTML$,
 75,
 84,
 930,
 false,
 0,
 NOW(),
 '{"name": "化学平衡", "description": "可逆反应的化学平衡状态模拟", "difficulty": "medium", "render_mode": "html"}');


-- [10/24] 血液循环 (medicine, 75分)
INSERT INTO simulator_templates
(subject, topic, code, quality_score, visual_elements, line_count, has_setup_update, variable_count, created_at, metadata)
VALUES
('medicine',
 '血液循环',
 $HTML$<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>血液循环系统 - 医学模拟器</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background: #1E293B;
            font-family: 'Arial', sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        #canvas {
            border: 2px solid #334155;
            box-shadow: 0 0 20px rgba(220, 38, 38, 0.3);
        }
    </style>
</head>
<body>
    <canvas id="canvas" width="1200" height="800"></canvas>

    <script>
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');

        // 医学配色方案
        const COLORS = {
            primary: '#DC2626',      // 红色 - 动脉血
            secondary: '#2563EB',    // 蓝色 - 静脉血
            accent: '#10B981',       // 绿色 - 心脏/器官
            background: '#1E293B',
            text: '#F1F5F9',
            arterial: '#DC2626',     // 氧合血
            venous: '#2563EB',       // 缺氧血
            heart: '#10B981',
            lung: '#8B5CF6',         // 紫色 - 肺
            organ: '#F59E0B'         // 橙色 - 其他器官
        };

        // 比例坐标系统
        const scale = {
            width: canvas.width,
            height: canvas.height,
            heartX: canvas.width * 0.5,
            heartY: canvas.height * 0.4,
            heartSize: Math.min(canvas.width, canvas.height) * 0.12,
            lungOffsetX: canvas.width * 0.15,
            lungY: canvas.height * 0.25,
            organY: canvas.height * 0.65
        };

        // 模拟器状态
        let time = 0;
        let heartRate = 72; // 每分钟心跳次数
        let beatPhase = 0; // 0-1: 心脏收缩舒张相位

        // 平滑显示值
        let displayHeartRate = 72;

        // 速度控制
        const speedOptions = [0.25, 0.5, 1, 2, 4];
        let currentSpeedIndex = 2; // 默认 1x
        let playbackSpeed = 1.0;

        // 拖拽状态
        let isDragging = false;

        // 血液粒子系统
        const bloodCells = [];
        const maxBloodCells = 200;

        // 缓动函数 - 3种类型
        const easing = {
            // 线性 - 匀速流动
            linear: (t) => t,

            // easeInOut - 心脏收缩舒张
            easeInOut: (t) => {
                return t < 0.5
                    ? 2 * t * t
                    : 1 - Math.pow(-2 * t + 2, 2) / 2;
            },

            // easeOutBounce - 心脏跳动反馈
            easeOutBounce: (t) => {
                const n1 = 7.5625;
                const d1 = 2.75;
                if (t < 1 / d1) {
                    return n1 * t * t;
                } else if (t < 2 / d1) {
                    return n1 * (t -= 1.5 / d1) * t + 0.75;
                } else if (t < 2.5 / d1) {
                    return n1 * (t -= 2.25 / d1) * t + 0.9375;
                } else {
                    return n1 * (t -= 2.625 / d1) * t + 0.984375;
                }
            },

            // harmonic - 节律性心跳
            harmonic: (t) => {
                return (Math.sin(t * Math.PI * 2 - Math.PI / 2) + 1) / 2;
            }
        };

        // 血液粒子类
        class BloodCell {
            constructor(path, isArterial) {
                this.path = path; // 'systemic' | 'pulmonary'
                this.isArterial = isArterial;
                this.progress = Math.random();
                this.speed = 0.01 + Math.random() * 0.01;
                this.size = 3 + Math.random() * 2;
                this.alpha = 0.6 + Math.random() * 0.4;
                this.glowIntensity = 0;
            }

            update(dt) {
                this.progress += this.speed * (heartRate / 72) * dt * playbackSpeed;
                if (this.progress >= 1) {
                    this.progress = 0;
                    // 氧气交换
                    if (this.path === 'pulmonary') {
                        this.isArterial = !this.isArterial;
                        this.glowIntensity = 1; // 氧气交换时发光
                    } else if (this.path === 'systemic') {
                        this.isArterial = !this.isArterial;
                    }
                }

                // 发光衰减
                this.glowIntensity *= 0.95;
            }

            getPosition() {
                const pos = this.path === 'systemic'
                    ? getSystemicCirculationPath(this.progress, this.isArterial)
                    : getPulmonaryCirculationPath(this.progress, this.isArterial);
                return pos;
            }

            draw() {
                const pos = this.getPosition();
                const color = this.isArterial ? COLORS.arterial : COLORS.venous;

                // 发光效果
                if (this.glowIntensity > 0.1) {
                    const gradient = ctx.createRadialGradient(pos.x, pos.y, 0, pos.x, pos.y, this.size * 3);
                    gradient.addColorStop(0, color + 'FF');
                    gradient.addColorStop(0.5, color + '66');
                    gradient.addColorStop(1, color + '00');
                    ctx.fillStyle = gradient;
                    ctx.fillRect(pos.x - this.size * 3, pos.y - this.size * 3, this.size * 6, this.size * 6);
                }

                // 粒子本体
                ctx.globalAlpha = this.alpha;
                ctx.fillStyle = color;
                ctx.beginPath();
                ctx.arc(pos.x, pos.y, this.size, 0, Math.PI * 2);
                ctx.fill();
                ctx.globalAlpha = 1;
            }
        }

        // 辅助函数集合 (12+个)

        // 1. 体循环路径计算
        function getSystemicCirculationPath(t, isArterial) {
            const heartX = scale.heartX;
            const heartY = scale.heartY;

            if (isArterial) {
                // 动脉：心脏 -> 全身器官
                if (t < 0.3) {
                    // 从心脏出发（主动脉）
                    const progress = t / 0.3;
                    return {
                        x: heartX,
                        y: heartY + progress * (scale.organY - heartY) * 0.5
                    };
                } else if (t < 0.6) {
                    // 到达器官
                    const progress = (t - 0.3) / 0.3;
                    const angle = progress * Math.PI * 2;
                    return {
                        x: heartX + Math.cos(angle) * scale.width * 0.25,
                        y: scale.organY + Math.sin(angle) * scale.height * 0.15
                    };
                } else {
                    // 返回路径准备
                    const progress = (t - 0.6) / 0.4;
                    const angle = Math.PI * 2 + progress * Math.PI;
                    return {
                        x: heartX + Math.cos(angle) * scale.width * 0.25 * (1 - progress * 0.5),
                        y: scale.organY + Math.sin(angle) * scale.height * 0.15
                    };
                }
            } else {
                // 静脉：器官 -> 心脏
                if (t < 0.4) {
                    const progress = t / 0.4;
                    const angle = Math.PI + progress * Math.PI;
                    return {
                        x: heartX + Math.cos(angle) * scale.width * 0.25 * (1 - progress),
                        y: scale.organY - progress * (scale.organY - heartY) * 0.3
                    };
                } else {
                    const progress = (t - 0.4) / 0.6;
                    return {
                        x: heartX + (1 - progress) * scale.width * 0.1,
                        y: heartY + (1 - progress) * scale.height * 0.1
                    };
                }
            }
        }

        // 2. 肺循环路径计算
        function getPulmonaryCirculationPath(t, isArterial) {
            const heartX = scale.heartX;
            const heartY = scale.heartY;
            const lungY = scale.lungY;

            if (!isArterial) {
                // 肺动脉：心脏 -> 肺（携带缺氧血）
                if (t < 0.5) {
                    const progress = t / 0.5;
                    const side = Math.random() > 0.5 ? 1 : -1;
                    return {
                        x: heartX + easing.easeInOut(progress) * scale.lungOffsetX * side,
                        y: heartY - progress * (heartY - lungY)
                    };
                } else {
                    const progress = (t - 0.5) / 0.5;
                    const side = Math.random() > 0.5 ? 1 : -1;
                    return {
                        x: heartX + scale.lungOffsetX * side,
                        y: lungY + Math.sin(progress * Math.PI) * scale.height * 0.05
                    };
                }
            } else {
                // 肺静脉：肺 -> 心脏（携带氧合血）
                if (t < 0.5) {
                    const progress = t / 0.5;
                    const side = Math.random() > 0.5 ? 1 : -1;
                    return {
                        x: heartX + scale.lungOffsetX * side * (1 - progress * 0.5),
                        y: lungY + Math.sin(progress * Math.PI) * scale.height * 0.05
                    };
                } else {
                    const progress = (t - 0.5) / 0.5;
                    const side = Math.random() > 0.5 ? 1 : -1;
                    return {
                        x: heartX + scale.lungOffsetX * side * 0.5 * (1 - progress),
                        y: lungY + progress * (heartY - lungY)
                    };
                }
            }
        }

        // 3. 绘制心脏（复合对象）
        function drawHeart() {
            const x = scale.heartX;
            const y = scale.heartY;
            const size = scale.heartSize * (1 + beatPhase * 0.15); // 跳动效果

            // 心脏主体
            ctx.save();
            ctx.translate(x, y);

            // 发光效果
            const glowGradient = ctx.createRadialGradient(0, 0, size * 0.5, 0, 0, size * 1.5);
            glowGradient.addColorStop(0, COLORS.heart + '66');
            glowGradient.addColorStop(1, COLORS.heart + '00');
            ctx.fillStyle = glowGradient;
            ctx.fillRect(-size * 1.5, -size * 1.5, size * 3, size * 3);

            // 心脏形状
            ctx.fillStyle = COLORS.heart;
            ctx.beginPath();
            ctx.moveTo(0, size * 0.3);

            // 左心形曲线
            ctx.bezierCurveTo(-size, -size * 0.3, -size, -size, 0, -size * 0.3);
            // 右心形曲线
            ctx.bezierCurveTo(size, -size, size, -size * 0.3, 0, size * 0.3);
            ctx.fill();

            // 心腔分隔
            ctx.strokeStyle = COLORS.background;
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.moveTo(0, -size * 0.3);
            ctx.lineTo(0, size * 0.3);
            ctx.stroke();

            // 标签
            ctx.fillStyle = COLORS.text;
            ctx.font = 'bold 16px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('心脏', 0, size * 1.3);

            ctx.restore();
        }

        // 4. 绘制肺部（复合对象）
        function drawLungs() {
            const centerX = scale.heartX;
            const y = scale.lungY;
            const size = scale.heartSize * 0.8;

            // 左肺
            drawSingleLung(centerX - scale.lungOffsetX, y, size, '左肺');
            // 右肺
            drawSingleLung(centerX + scale.lungOffsetX, y, size, '右肺');
        }

        // 5. 绘制单个肺（辅助函数）
        function drawSingleLung(x, y, size, label) {
            ctx.save();
            ctx.translate(x, y);

            // 肺部轮廓
            ctx.fillStyle = COLORS.lung + '40';
            ctx.strokeStyle = COLORS.lung;
            ctx.lineWidth = 2;

            ctx.beginPath();
            ctx.ellipse(0, 0, size * 0.7, size, 0, 0, Math.PI * 2);
            ctx.fill();
            ctx.stroke();

            // 肺泡纹理
            for (let i = 0; i < 5; i++) {
                const angle = (i / 5) * Math.PI * 2;
                const r = size * 0.4;
                ctx.beginPath();
                ctx.arc(Math.cos(angle) * r * 0.5, Math.sin(angle) * r * 0.7, size * 0.2, 0, Math.PI * 2);
                ctx.stroke();
            }

            // 标签
            ctx.fillStyle = COLORS.text;
            ctx.font = '14px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(label, 0, size * 1.3);

            ctx.restore();
        }

        // 6. 绘制器官（复合对象）
        function drawOrgans() {
            const y = scale.organY;
            const centerX = scale.heartX;
            const size = scale.heartSize * 0.5;

            // 绘制多个器官
            const organs = [
                { name: '脑', angle: -Math.PI / 2, color: COLORS.organ },
                { name: '肝', angle: -Math.PI / 6, color: '#B45309' },
                { name: '肾', angle: Math.PI / 6, color: '#9333EA' },
                { name: '肠', angle: Math.PI / 2, color: '#DC2626' }
            ];

            organs.forEach(organ => {
                const x = centerX + Math.cos(organ.angle) * scale.width * 0.25;
                const oy = y + Math.sin(organ.angle) * scale.height * 0.15;

                ctx.fillStyle = organ.color + '60';
                ctx.strokeStyle = organ.color;
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.arc(x, oy, size, 0, Math.PI * 2);
                ctx.fill();
                ctx.stroke();

                ctx.fillStyle = COLORS.text;
                ctx.font = '12px Arial';
                ctx.textAlign = 'center';
                ctx.fillText(organ.name, x, oy + size + 15);
            });
        }

        // 7. 绘制血管网络
        function drawVessels() {
            ctx.strokeStyle = COLORS.arterial + '40';
            ctx.lineWidth = 6;
            ctx.lineCap = 'round';

            // 主动脉
            drawVesselPath([
                { x: scale.heartX, y: scale.heartY },
                { x: scale.heartX, y: scale.organY - scale.height * 0.1 }
            ]);

            // 动脉分支
            const branches = 4;
            for (let i = 0; i < branches; i++) {
                const angle = (i / branches) * Math.PI * 2 - Math.PI / 2;
                const endX = scale.heartX + Math.cos(angle) * scale.width * 0.25;
                const endY = scale.organY + Math.sin(angle) * scale.height * 0.15;

                ctx.strokeStyle = COLORS.arterial + '30';
                ctx.lineWidth = 4;
                drawVesselPath([
                    { x: scale.heartX, y: scale.organY - scale.height * 0.1 },
                    { x: endX, y: endY }
                ]);
            }

            // 肺动脉
            ctx.strokeStyle = COLORS.venous + '40';
            ctx.lineWidth = 5;
            drawVesselPath([
                { x: scale.heartX, y: scale.heartY },
                { x: scale.heartX - scale.lungOffsetX, y: scale.lungY }
            ]);
            drawVesselPath([
                { x: scale.heartX, y: scale.heartY },
                { x: scale.heartX + scale.lungOffsetX, y: scale.lungY }
            ]);

            // 肺静脉
            ctx.strokeStyle = COLORS.arterial + '40';
            drawVesselPath([
                { x: scale.heartX - scale.lungOffsetX, y: scale.lungY },
                { x: scale.heartX, y: scale.heartY - scale.heartSize * 0.5 }
            ]);
            drawVesselPath([
                { x: scale.heartX + scale.lungOffsetX, y: scale.lungY },
                { x: scale.heartX, y: scale.heartY - scale.heartSize * 0.5 }
            ]);
        }

        // 8. 绘制血管路径（辅助函数）
        function drawVesselPath(points) {
            ctx.beginPath();
            ctx.moveTo(points[0].x, points[0].y);
            for (let i = 1; i < points.length; i++) {
                ctx.lineTo(points[i].x, points[i].y);
            }
            ctx.stroke();
        }

        // 9. 更新心跳相位
        function updateHeartBeat(dt) {
            const bpm = heartRate / 60; // 每秒心跳
            const cycleTime = 1 / bpm; // 一个心跳周期（秒）
            beatPhase = easing.harmonic((time % cycleTime) / cycleTime);
        }

        // 10. 绘制UI控制面板
        function drawControlPanel() {
            const panelX = scale.width * 0.05;
            const panelY = scale.height * 0.05;
            const panelWidth = scale.width * 0.25;
            const panelHeight = scale.height * 0.35;

            // 面板背景
            ctx.fillStyle = 'rgba(30, 41, 59, 0.9)';
            ctx.strokeStyle = COLORS.accent;
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.roundRect(panelX, panelY, panelWidth, panelHeight, 10);
            ctx.fill();
            ctx.stroke();

            // 标题
            ctx.fillStyle = COLORS.text;
            ctx.font = 'bold 18px Arial';
            ctx.textAlign = 'left';
            ctx.fillText('血液循环系统', panelX + 15, panelY + 30);

            // 心率滑块
            ctx.font = '14px Arial';
            ctx.fillText(`心率: ${Math.round(displayHeartRate)} BPM`, panelX + 15, panelY + 60);
            drawSlider(panelX + 15, panelY + 75, panelWidth - 30, displayHeartRate, 40, 150, COLORS.heart);

            // 心跳相位指示器
            ctx.fillText('心脏状态:', panelX + 15, panelY + 110);
            const phaseBarX = panelX + 15;
            const phaseBarY = panelY + 120;
            const phaseBarWidth = panelWidth - 30;
            const phaseBarHeight = 20;

            ctx.fillStyle = '#334155';
            ctx.fillRect(phaseBarX, phaseBarY, phaseBarWidth, phaseBarHeight);

            ctx.fillStyle = COLORS.heart;
            ctx.fillRect(phaseBarX, phaseBarY, phaseBarWidth * beatPhase, phaseBarHeight);

            ctx.strokeStyle = COLORS.accent;
            ctx.lineWidth = 2;
            ctx.strokeRect(phaseBarX, phaseBarY, phaseBarWidth, phaseBarHeight);

            // 血液粒子计数
            ctx.fillStyle = COLORS.text;
            ctx.fillText(`血细胞: ${bloodCells.length}`, panelX + 15, panelY + 160);

            // 说明
            ctx.font = '12px Arial';
            ctx.fillStyle = COLORS.text + 'CC';
            ctx.fillText('红色 = 氧合血', panelX + 15, panelY + 190);
            ctx.fillText('蓝色 = 缺氧血', panelX + 15, panelY + 210);
            ctx.fillText('拖拽滑块调节心率', panelX + 15, panelY + 230);
            ctx.fillText('上/下键: ±5 BPM', panelX + 15, panelY + 250);
        }

        // 辅助函数：绘制滑块
        function drawSlider(x, y, w, value, min, max, color) {
            // 轨道
            ctx.strokeStyle = '#334155';
            ctx.lineWidth = 4;
            ctx.lineCap = 'round';
            ctx.beginPath();
            ctx.moveTo(x, y);
            ctx.lineTo(x + w, y);
            ctx.stroke();

            // 进度
            const progress = (value - min) / (max - min);
            ctx.strokeStyle = color;
            ctx.lineWidth = 4;
            ctx.beginPath();
            ctx.moveTo(x, y);
            ctx.lineTo(x + w * progress, y);
            ctx.stroke();

            // 手柄
            ctx.fillStyle = color;
            ctx.shadowColor = color;
            ctx.shadowBlur = 15;
            ctx.beginPath();
            ctx.arc(x + w * progress, y, 8, 0, Math.PI * 2);
            ctx.fill();
            ctx.shadowBlur = 0;
        }

        // 绘制速度控制面板
        function drawSpeedControl() {
            const panelX = scale.width * 0.05;
            const panelY = scale.height * 0.44;
            const panelWidth = scale.width * 0.25;
            const panelHeight = scale.height * 0.12;

            // 面板背景
            ctx.fillStyle = 'rgba(30, 41, 59, 0.9)';
            ctx.strokeStyle = COLORS.primary;
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.roundRect(panelX, panelY, panelWidth, panelHeight, 10);
            ctx.fill();
            ctx.stroke();

            // 标题
            ctx.fillStyle = COLORS.text;
            ctx.font = '14px Arial';
            ctx.textAlign = 'left';
            ctx.fillText('播放速度:', panelX + 15, panelY + 25);

            // 速度按钮
            const buttonWidth = 45;
            const buttonHeight = 28;
            const buttonSpacing = 6;
            const startX = panelX + 15;
            const buttonY = panelY + 40;

            speedOptions.forEach((speed, index) => {
                const buttonX = startX + index * (buttonWidth + buttonSpacing);
                const isActive = currentSpeedIndex === index;

                // 按钮背景
                ctx.fillStyle = isActive ? COLORS.accent : '#334155';
                ctx.globalAlpha = isActive ? 1.0 : 0.5;
                ctx.fillRect(buttonX, buttonY, buttonWidth, buttonHeight);
                ctx.globalAlpha = 1.0;

                // 按钮边框
                ctx.strokeStyle = isActive ? COLORS.accent : '#475569';
                ctx.lineWidth = 2;
                if (isActive) {
                    ctx.shadowColor = COLORS.accent;
                    ctx.shadowBlur = 10;
                }
                ctx.strokeRect(buttonX, buttonY, buttonWidth, buttonHeight);
                ctx.shadowBlur = 0;

                // 按钮文字
                ctx.fillStyle = COLORS.text;
                ctx.font = '12px Arial';
                ctx.textAlign = 'center';
                const label = speed === 1 ? '1x' : speed < 1 ? `${speed}x` : `${speed}x`;
                ctx.fillText(label, buttonX + buttonWidth / 2, buttonY + buttonHeight / 2 + 4);
            });

            ctx.textAlign = 'left';
        }

        // 11. 绘制标注箭头
        function drawAnnotations() {
            const annotations = [
                {
                    text: '体循环',
                    x: scale.width * 0.75,
                    y: scale.organY,
                    color: COLORS.arterial
                },
                {
                    text: '肺循环',
                    x: scale.width * 0.25,
                    y: scale.lungY,
                    color: COLORS.lung
                }
            ];

            annotations.forEach(ann => {
                ctx.save();

                // 箭头
                drawArrow(
                    ann.x - 30,
                    ann.y,
                    ann.x - 70,
                    ann.y,
                    ann.color
                );

                // 文字
                ctx.fillStyle = COLORS.text;
                ctx.font = 'bold 14px Arial';
                ctx.textAlign = 'right';
                ctx.fillText(ann.text, ann.x - 80, ann.y + 5);

                ctx.restore();
            });
        }

        // 12. 绘制箭头（辅助函数）
        function drawArrow(fromX, fromY, toX, toY, color) {
            const headlen = 10;
            const angle = Math.atan2(toY - fromY, toX - fromX);

            ctx.strokeStyle = color;
            ctx.fillStyle = color;
            ctx.lineWidth = 2;

            // 线条
            ctx.beginPath();
            ctx.moveTo(fromX, fromY);
            ctx.lineTo(toX, toY);
            ctx.stroke();

            // 箭头
            ctx.beginPath();
            ctx.moveTo(toX, toY);
            ctx.lineTo(
                toX - headlen * Math.cos(angle - Math.PI / 6),
                toY - headlen * Math.sin(angle - Math.PI / 6)
            );
            ctx.lineTo(
                toX - headlen * Math.cos(angle + Math.PI / 6),
                toY - headlen * Math.sin(angle + Math.PI / 6)
            );
            ctx.closePath();
            ctx.fill();
        }

        // 13. 初始化血液粒子
        function initBloodCells() {
            for (let i = 0; i < maxBloodCells / 2; i++) {
                bloodCells.push(new BloodCell('systemic', i % 2 === 0));
            }
            for (let i = 0; i < maxBloodCells / 2; i++) {
                bloodCells.push(new BloodCell('pulmonary', i % 2 === 0));
            }
        }

        // 14. 心率调整（交互函数）
        function adjustHeartRate(delta) {
            heartRate = Math.max(40, Math.min(150, heartRate + delta));
        }

        // 15. 绘制图例
        function drawLegend() {
            const legendX = scale.width * 0.8;
            const legendY = scale.height * 0.85;

            const items = [
                { color: COLORS.arterial, text: '动脉血（氧合）' },
                { color: COLORS.venous, text: '静脉血（缺氧）' },
                { color: COLORS.heart, text: '心脏' },
                { color: COLORS.lung, text: '肺' }
            ];

            items.forEach((item, i) => {
                const y = legendY + i * 25;

                ctx.fillStyle = item.color;
                ctx.beginPath();
                ctx.arc(legendX, y, 6, 0, Math.PI * 2);
                ctx.fill();

                ctx.fillStyle = COLORS.text;
                ctx.font = '12px Arial';
                ctx.textAlign = 'left';
                ctx.fillText(item.text, legendX + 15, y + 4);
            });
        }

        // 主渲染循环
        function render() {
            // 清空画布
            ctx.fillStyle = COLORS.background;
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // 绘制血管网络
            drawVessels();

            // 绘制器官
            drawOrgans();
            drawLungs();

            // 绘制血液粒子
            bloodCells.forEach(cell => cell.draw());

            // 绘制心脏（最上层）
            drawHeart();

            // 绘制注释
            drawAnnotations();

            // 绘制UI
            drawControlPanel();
            drawSpeedControl();
            drawLegend();
        }

        // 主更新循环
        let lastTime = 0;
        function update(currentTime) {
            const dt = Math.min((currentTime - lastTime) / 1000, 0.1); // 限制最大dt
            lastTime = currentTime;

            // 更新播放速度
            playbackSpeed = speedOptions[currentSpeedIndex];

            // 平滑插值心率显示
            const smoothFactor = 0.2;
            displayHeartRate = displayHeartRate * (1 - smoothFactor) + heartRate * smoothFactor;

            time += dt * playbackSpeed;

            // 更新心跳
            updateHeartBeat(dt);

            // 更新血液粒子
            bloodCells.forEach(cell => cell.update(dt));

            render();
            requestAnimationFrame(update);
        }

        // 交互：拖拽滑块调节心率
        canvas.addEventListener('mousedown', (e) => {
            const rect = canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const panelX = scale.width * 0.05;
            const panelY = scale.height * 0.05;
            const panelWidth = scale.width * 0.25;
            const sliderY = panelY + 75;
            const sliderWidth = panelWidth - 30;

            // 检查是否点击滑块
            if (x >= panelX + 15 && x <= panelX + 15 + sliderWidth &&
                y >= sliderY - 10 && y <= sliderY + 10) {
                isDragging = true;
            }

            // 检查速度按钮
            const speedPanelX = scale.width * 0.05;
            const speedPanelY = scale.height * 0.44;
            const buttonWidth = 45;
            const buttonHeight = 28;
            const buttonSpacing = 6;
            const startX = speedPanelX + 15;
            const buttonY = speedPanelY + 40;

            speedOptions.forEach((speed, index) => {
                const buttonX = startX + index * (buttonWidth + buttonSpacing);
                if (x >= buttonX && x <= buttonX + buttonWidth &&
                    y >= buttonY && y <= buttonY + buttonHeight) {
                    currentSpeedIndex = index;
                }
            });
        });

        canvas.addEventListener('mousemove', (e) => {
            if (isDragging) {
                const rect = canvas.getBoundingClientRect();
                const x = e.clientX - rect.left;

                const panelX = scale.width * 0.05;
                const panelWidth = scale.width * 0.25;
                const sliderWidth = panelWidth - 30;
                const sliderX = panelX + 15;

                const progress = Math.max(0, Math.min(1, (x - sliderX) / sliderWidth));
                heartRate = 40 + progress * 110; // 40-150 BPM
            }
        });

        canvas.addEventListener('mouseup', () => {
            isDragging = false;
        });

        // 交互：键盘控制心率
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowUp') {
                adjustHeartRate(5);
            } else if (e.key === 'ArrowDown') {
                adjustHeartRate(-5);
            }
        });

        // 初始化并启动
        initBloodCells();
        requestAnimationFrame(update);

        console.log('血液循环系统模拟器已启动');
        console.log('控制说明：');
        console.log('- 拖拽滑块：调整心率');
        console.log('- 上/下方向键：调整心率 ±5 BPM');
        console.log('- 点击速度按钮：切换播放速度');
    </script>
</body>
</html>$HTML$,
 75,
 175,
 841,
 false,
 0,
 NOW(),
 '{"name": "血液循环", "description": "心血管系统的血液循环路径和心脏泵血过程", "difficulty": "medium", "render_mode": "html"}');


-- [11/24] 免疫应答 (medicine, 75分)
INSERT INTO simulator_templates
(subject, topic, code, quality_score, visual_elements, line_count, has_setup_update, variable_count, created_at, metadata)
VALUES
('medicine',
 '免疫应答',
 $HTML$<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>免疫应答过程 - 医学模拟器</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background: #1E293B;
            font-family: 'Arial', sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        #canvas {
            border: 2px solid #334155;
            box-shadow: 0 0 20px rgba(220, 38, 38, 0.3);
        }
    </style>
</head>
<body>
    <canvas id="canvas" width="1200" height="800"></canvas>

    <script>
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');

        // 医学配色方案
        const COLORS = {
            primary: '#DC2626',
            secondary: '#2563EB',
            accent: '#10B981',
            background: '#1E293B',
            text: '#F1F5F9',
            antigen: '#DC2626',
            antibody: '#2563EB',
            phagocyte: '#10B981',
            tcell: '#8B5CF6',
            bcell: '#F59E0B',
            bound: '#EC4899'
        };

        const scale = {
            width: canvas.width,
            height: canvas.height,
            centerX: canvas.width * 0.5,
            centerY: canvas.height * 0.5,
            areaSize: Math.min(canvas.width, canvas.height) * 0.7
        };

        // 状态
        let time = 0;
        let immuneStrength = 50;
        let displayImmuneStrength = 50;

        // 速度控制
        const speedOptions = [0.25, 0.5, 1, 2, 4];
        let currentSpeedIndex = 2;
        let playbackSpeed = 1.0;

        // 拖拽状态
        let isDragging = false;

        // 实体数组
        const antigens = [];
        const antibodies = [];
        const phagocytes = [];
        const tcells = [];
        const bcells = [];

        const MAX_ANTIGENS = 30;
        const MAX_ANTIBODIES = 50;
        const MAX_PHAGOCYTES = 8;
        const MAX_TCELLS = 6;
        const MAX_BCELLS = 6;

        // 抗原类
        class Antigen {
            constructor() {
                this.x = scale.centerX + (Math.random() - 0.5) * scale.areaSize;
                this.y = scale.centerY + (Math.random() - 0.5) * scale.areaSize;
                this.vx = (Math.random() - 0.5) * 50;
                this.vy = (Math.random() - 0.5) * 50;
                this.size = 8 + Math.random() * 4;
                this.rotation = Math.random() * Math.PI * 2;
                this.rotationSpeed = (Math.random() - 0.5) * 2;
                this.targetedBy = null;
                this.health = 100;
            }

            update(dt) {
                if (this.health > 0 && !this.targetedBy) {
                    // 布朗运动
                    this.vx += (Math.random() - 0.5) * 100 * dt;
                    this.vy += (Math.random() - 0.5) * 100 * dt;

                    const speed = Math.sqrt(this.vx * this.vx + this.vy * this.vy);
                    if (speed > 80) {
                        this.vx *= 80 / speed;
                        this.vy *= 80 / speed;
                    }

                    this.x += this.vx * dt;
                    this.y += this.vy * dt;

                    // 边界反弹
                    const margin = 50;
                    if (this.x < margin) { this.x = margin; this.vx = Math.abs(this.vx); }
                    if (this.x > scale.width - margin) { this.x = scale.width - margin; this.vx = -Math.abs(this.vx); }
                    if (this.y < margin) { this.y = margin; this.vy = Math.abs(this.vy); }
                    if (this.y > scale.height - margin) { this.y = scale.height - margin; this.vy = -Math.abs(this.vy); }

                    this.rotation += this.rotationSpeed * dt;
                }
            }

            draw() {
                if (this.health <= 0) return;

                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.rotation);

                ctx.fillStyle = COLORS.antigen;
                ctx.strokeStyle = COLORS.text;
                ctx.lineWidth = 1;

                ctx.beginPath();
                ctx.arc(0, 0, this.size, 0, Math.PI * 2);
                ctx.fill();
                ctx.stroke();

                // 刺突
                const spikes = 8;
                for (let i = 0; i < spikes; i++) {
                    const angle = (i / spikes) * Math.PI * 2;
                    const spikeLength = this.size * 0.6;
                    ctx.beginPath();
                    ctx.moveTo(Math.cos(angle) * this.size, Math.sin(angle) * this.size);
                    ctx.lineTo(Math.cos(angle) * (this.size + spikeLength), Math.sin(angle) * (this.size + spikeLength));
                    ctx.lineWidth = 2;
                    ctx.stroke();
                }

                ctx.restore();
            }
        }

        // 抗体类
        class Antibody {
            constructor(sourceX, sourceY) {
                this.x = sourceX + (Math.random() - 0.5) * 30;
                this.y = sourceY + (Math.random() - 0.5) * 30;
                this.vx = (Math.random() - 0.5) * 100;
                this.vy = (Math.random() - 0.5) * 100;
                this.size = 6;
                this.targetAntigen = null;
                this.attacking = false;
            }

            update(dt) {
                if (!this.attacking) {
                    // 寻找最近的抗原
                    let nearest = null;
                    let minDist = Infinity;

                    for (let ag of antigens) {
                        if (ag.health > 0 && !ag.targetedBy) {
                            const dist = Math.sqrt((ag.x - this.x) ** 2 + (ag.y - this.y) ** 2);
                            if (dist < minDist) {
                                minDist = dist;
                                nearest = ag;
                            }
                        }
                    }

                    if (nearest && minDist < 200) {
                        const dx = nearest.x - this.x;
                        const dy = nearest.y - this.y;
                        const angle = Math.atan2(dy, dx);
                        this.vx += Math.cos(angle) * 150 * dt;
                        this.vy += Math.sin(angle) * 150 * dt;
                        this.targetAntigen = nearest;

                        // 检测结合
                        if (minDist < 15) {
                            this.attacking = true;
                            nearest.targetedBy = this;
                            nearest.health -= 50 * dt * playbackSpeed; // 持续伤害
                        }
                    } else {
                        this.vx += (Math.random() - 0.5) * 50 * dt;
                        this.vy += (Math.random() - 0.5) * 50 * dt;
                    }

                    const speed = Math.sqrt(this.vx * this.vx + this.vy * this.vy);
                    if (speed > 120) {
                        this.vx *= 120 / speed;
                        this.vy *= 120 / speed;
                    }

                    this.x += this.vx * dt;
                    this.y += this.vy * dt;

                    this.x = Math.max(30, Math.min(scale.width - 30, this.x));
                    this.y = Math.max(30, Math.min(scale.height - 30, this.y));
                } else {
                    // 跟随目标
                    if (this.targetAntigen && this.targetAntigen.health > 0) {
                        this.x = this.targetAntigen.x + 15;
                        this.y = this.targetAntigen.y;
                        this.targetAntigen.health -= 30 * dt * playbackSpeed;
                    } else {
                        this.attacking = false;
                        this.targetAntigen = null;
                    }
                }
            }

            draw() {
                if (this.attacking) return;

                ctx.save();
                ctx.translate(this.x, this.y);

                ctx.strokeStyle = COLORS.antibody;
                ctx.fillStyle = COLORS.antibody;
                ctx.lineWidth = 3;
                ctx.lineCap = 'round';

                const stemLength = this.size * 2;
                const armLength = this.size * 1.5;
                const armAngle = Math.PI / 6;

                ctx.beginPath();
                ctx.moveTo(0, stemLength);
                ctx.lineTo(0, 0);
                ctx.stroke();

                ctx.beginPath();
                ctx.moveTo(0, 0);
                ctx.lineTo(-Math.sin(armAngle) * armLength, -Math.cos(armAngle) * armLength);
                ctx.stroke();

                ctx.beginPath();
                ctx.moveTo(0, 0);
                ctx.lineTo(Math.sin(armAngle) * armLength, -Math.cos(armAngle) * armLength);
                ctx.stroke();

                ctx.restore();
            }
        }

        // 吞噬细胞类
        class Phagocyte {
            constructor() {
                this.x = 50 + Math.random() * (scale.width - 100);
                this.y = 50 + Math.random() * (scale.height - 100);
                this.vx = (Math.random() - 0.5) * 40;
                this.vy = (Math.random() - 0.5) * 40;
                this.size = 20;
            }

            update(dt) {
                // 寻找受伤的抗原
                let nearest = null;
                let minDist = Infinity;

                for (let ag of antigens) {
                    if (ag.health < 100 && ag.health > 0) {
                        const dist = Math.sqrt((ag.x - this.x) ** 2 + (ag.y - this.y) ** 2);
                        if (dist < minDist) {
                            minDist = dist;
                            nearest = ag;
                        }
                    }
                }

                if (nearest && minDist < 250) {
                    const dx = nearest.x - this.x;
                    const dy = nearest.y - this.y;
                    const angle = Math.atan2(dy, dx);
                    this.vx += Math.cos(angle) * 100 * dt;
                    this.vy += Math.sin(angle) * 100 * dt;

                    // 吞噬
                    if (minDist < this.size + 10) {
                        nearest.health -= 80 * dt * playbackSpeed;
                    }
                } else {
                    this.vx += (Math.random() - 0.5) * 30 * dt;
                    this.vy += (Math.random() - 0.5) * 30 * dt;
                }

                const speed = Math.sqrt(this.vx * this.vx + this.vy * this.vy);
                if (speed > 60) {
                    this.vx *= 60 / speed;
                    this.vy *= 60 / speed;
                }

                this.x += this.vx * dt;
                this.y += this.vy * dt;

                this.x = Math.max(this.size, Math.min(scale.width - this.size, this.x));
                this.y = Math.max(this.size, Math.min(scale.height - this.size, this.y));
            }

            draw() {
                ctx.save();
                ctx.translate(this.x, this.y);

                ctx.fillStyle = COLORS.phagocyte;
                ctx.strokeStyle = COLORS.text;
                ctx.lineWidth = 2;

                ctx.beginPath();
                const points = 8;
                for (let i = 0; i < points; i++) {
                    const angle = (i / points) * Math.PI * 2 + time * 0.5;
                    const r = this.size * (1 + Math.sin(angle * 3 + time) * 0.2);
                    const x = Math.cos(angle) * r;
                    const y = Math.sin(angle) * r;
                    if (i === 0) ctx.moveTo(x, y);
                    else ctx.lineTo(x, y);
                }
                ctx.closePath();
                ctx.fill();
                ctx.stroke();

                ctx.fillStyle = COLORS.text + '60';
                ctx.beginPath();
                ctx.arc(0, 0, this.size * 0.4, 0, Math.PI * 2);
                ctx.fill();

                ctx.restore();
            }
        }

        // T细胞类
        class TCell {
            constructor() {
                this.x = 50 + Math.random() * (scale.width - 100);
                this.y = 50 + Math.random() * (scale.height - 100);
                this.vx = (Math.random() - 0.5) * 60;
                this.vy = (Math.random() - 0.5) * 60;
                this.size = 15;
            }

            update(dt) {
                this.vx += (Math.random() - 0.5) * 40 * dt;
                this.vy += (Math.random() - 0.5) * 40 * dt;

                const speed = Math.sqrt(this.vx * this.vx + this.vy * this.vy);
                if (speed > 70) {
                    this.vx *= 70 / speed;
                    this.vy *= 70 / speed;
                }

                this.x += this.vx * dt;
                this.y += this.vy * dt;

                this.x = Math.max(this.size, Math.min(scale.width - this.size, this.x));
                this.y = Math.max(this.size, Math.min(scale.height - this.size, this.y));
            }

            draw() {
                ctx.save();
                ctx.translate(this.x, this.y);

                ctx.fillStyle = COLORS.tcell;
                ctx.strokeStyle = COLORS.text;
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.arc(0, 0, this.size, 0, Math.PI * 2);
                ctx.fill();
                ctx.stroke();

                const receptors = 4;
                for (let i = 0; i < receptors; i++) {
                    const angle = (i / receptors) * Math.PI * 2 + time;
                    const rx = Math.cos(angle) * this.size;
                    const ry = Math.sin(angle) * this.size;
                    ctx.fillStyle = COLORS.text;
                    ctx.beginPath();
                    ctx.arc(rx, ry, 3, 0, Math.PI * 2);
                    ctx.fill();
                }

                ctx.restore();
            }
        }

        // B细胞类
        class BCell {
            constructor() {
                this.x = 100 + Math.random() * (scale.width - 200);
                this.y = 100 + Math.random() * (scale.height - 200);
                this.vx = (Math.random() - 0.5) * 30;
                this.vy = (Math.random() - 0.5) * 30;
                this.size = 18;
                this.productionTimer = 0;
                this.productionRate = 1 + (immuneStrength / 100) * 2;
            }

            update(dt) {
                this.vx += (Math.random() - 0.5) * 20 * dt;
                this.vy += (Math.random() - 0.5) * 20 * dt;

                const speed = Math.sqrt(this.vx * this.vx + this.vy * this.vy);
                if (speed > 40) {
                    this.vx *= 40 / speed;
                    this.vy *= 40 / speed;
                }

                this.x += this.vx * dt;
                this.y += this.vy * dt;

                this.x = Math.max(this.size, Math.min(scale.width - this.size, this.x));
                this.y = Math.max(this.size, Math.min(scale.height - this.size, this.y));

                // 生产抗体
                this.productionTimer += dt;
                this.productionRate = 1 + (immuneStrength / 100) * 2;
                if (this.productionTimer >= 1 / this.productionRate && antibodies.length < MAX_ANTIBODIES) {
                    antibodies.push(new Antibody(this.x, this.y));
                    this.productionTimer = 0;
                }
            }

            draw() {
                ctx.save();
                ctx.translate(this.x, this.y);

                ctx.fillStyle = COLORS.bcell;
                ctx.strokeStyle = COLORS.text;
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.arc(0, 0, this.size, 0, Math.PI * 2);
                ctx.fill();
                ctx.stroke();

                ctx.strokeStyle = COLORS.text + '60';
                ctx.lineWidth = 1;
                for (let i = 0; i < 3; i++) {
                    ctx.beginPath();
                    ctx.arc(0, 0, this.size * (0.3 + i * 0.2), 0, Math.PI * 2);
                    ctx.stroke();
                }

                ctx.restore();
            }
        }

        // 初始化
        function init() {
            for (let i = 0; i < MAX_PHAGOCYTES; i++) phagocytes.push(new Phagocyte());
            for (let i = 0; i < MAX_TCELLS; i++) tcells.push(new TCell());
            for (let i = 0; i < MAX_BCELLS; i++) bcells.push(new BCell());
            for (let i = 0; i < 5; i++) antigens.push(new Antigen());
        }

        // 自动生成抗原
        function autoGenerateAntigens(dt) {
            const spawnRate = 0.3;
            if (Math.random() < spawnRate * dt && antigens.length < MAX_ANTIGENS * 0.7) {
                antigens.push(new Antigen());
            }
        }

        // 绘制背景网格
        function drawBackgroundGrid() {
            ctx.strokeStyle = COLORS.text + '10';
            ctx.lineWidth = 1;
            const gridSize = 50;
            for (let x = 0; x < scale.width; x += gridSize) {
                ctx.beginPath();
                ctx.moveTo(x, 0);
                ctx.lineTo(x, scale.height);
                ctx.stroke();
            }
            for (let y = 0; y < scale.height; y += gridSize) {
                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.lineTo(scale.width, y);
                ctx.stroke();
            }
        }

        // 绘制控制面板
        function drawControlPanel() {
            const panelX = scale.width * 0.02;
            const panelY = scale.height * 0.02;
            const panelWidth = scale.width * 0.22;
            const panelHeight = scale.height * 0.4;

            ctx.fillStyle = 'rgba(30, 41, 59, 0.95)';
            ctx.strokeStyle = COLORS.accent;
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.roundRect(panelX, panelY, panelWidth, panelHeight, 10);
            ctx.fill();
            ctx.stroke();

            ctx.fillStyle = COLORS.text;
            ctx.font = 'bold 18px Arial';
            ctx.textAlign = 'left';
            ctx.fillText('免疫应答系统', panelX + 15, panelY + 30);

            let yOffset = 60;

            // 统计信息
            const stats = [
                { label: '抗原', value: antigens.filter(a => a.health > 0).length, color: COLORS.antigen },
                { label: '抗体', value: antibodies.length, color: COLORS.antibody },
                { label: '吞噬细胞', value: phagocytes.length, color: COLORS.phagocyte },
                { label: 'T细胞', value: tcells.length, color: COLORS.tcell },
                { label: 'B细胞', value: bcells.length, color: COLORS.bcell }
            ];

            ctx.font = '13px Arial';
            stats.forEach((stat, i) => {
                const y = panelY + yOffset + i * 25;
                ctx.fillStyle = stat.color;
                ctx.beginPath();
                ctx.arc(panelX + 15, y, 5, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = COLORS.text;
                ctx.fillText(`${stat.label}: ${stat.value}`, panelX + 30, y + 4);
            });

            yOffset += stats.length * 25 + 20;

            // 免疫强度滑块
            ctx.fillStyle = COLORS.text;
            ctx.font = '13px Arial';
            ctx.fillText(`免疫强度: ${Math.round(displayImmuneStrength)}%`, panelX + 15, panelY + yOffset);

            yOffset += 20;

            const sliderX = panelX + 15;
            const sliderY = panelY + yOffset;
            const sliderWidth = panelWidth - 30;
            drawSlider(sliderX, sliderY, sliderWidth, displayImmuneStrength, 0, 100, COLORS.accent);

            yOffset += 35;

            // 操作说明
            ctx.fillStyle = COLORS.text + 'CC';
            ctx.font = '11px Arial';
            const instructions = [
                '点击右侧: 添加抗原',
                '拖拽滑块: 调节免疫力',
                'A键: 添加抗原'
            ];
            instructions.forEach((text, i) => {
                ctx.fillText(text, panelX + 15, panelY + yOffset + i * 18);
            });
        }

        // 绘制滑块
        function drawSlider(x, y, w, value, min, max, color) {
            ctx.strokeStyle = '#334155';
            ctx.lineWidth = 4;
            ctx.lineCap = 'round';
            ctx.beginPath();
            ctx.moveTo(x, y);
            ctx.lineTo(x + w, y);
            ctx.stroke();

            const progress = (value - min) / (max - min);
            const gradient = ctx.createLinearGradient(x, 0, x + w, 0);
            gradient.addColorStop(0, COLORS.antigen);
            gradient.addColorStop(0.5, COLORS.accent);
            gradient.addColorStop(1, COLORS.secondary);
            ctx.strokeStyle = gradient;
            ctx.lineWidth = 4;
            ctx.beginPath();
            ctx.moveTo(x, y);
            ctx.lineTo(x + w * progress, y);
            ctx.stroke();

            ctx.fillStyle = color;
            ctx.shadowColor = color;
            ctx.shadowBlur = 15;
            ctx.beginPath();
            ctx.arc(x + w * progress, y, 8, 0, Math.PI * 2);
            ctx.fill();
            ctx.shadowBlur = 0;
        }

        // 绘制速度控制
        function drawSpeedControl() {
            const panelX = scale.width * 0.02;
            const panelY = scale.height * 0.45;
            const panelWidth = scale.width * 0.22;
            const panelHeight = scale.height * 0.12;

            ctx.fillStyle = 'rgba(30, 41, 59, 0.95)';
            ctx.strokeStyle = COLORS.tcell;
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.roundRect(panelX, panelY, panelWidth, panelHeight, 10);
            ctx.fill();
            ctx.stroke();

            ctx.fillStyle = COLORS.text;
            ctx.font = '14px Arial';
            ctx.textAlign = 'left';
            ctx.fillText('播放速度:', panelX + 15, panelY + 25);

            const buttonWidth = 42;
            const buttonHeight = 28;
            const buttonSpacing = 5;
            const startX = panelX + 15;
            const buttonY = panelY + 40;

            speedOptions.forEach((speed, index) => {
                const buttonX = startX + index * (buttonWidth + buttonSpacing);
                const isActive = currentSpeedIndex === index;

                ctx.fillStyle = isActive ? COLORS.tcell : '#334155';
                ctx.globalAlpha = isActive ? 1.0 : 0.5;
                ctx.fillRect(buttonX, buttonY, buttonWidth, buttonHeight);
                ctx.globalAlpha = 1.0;

                ctx.strokeStyle = isActive ? COLORS.tcell : '#475569';
                ctx.lineWidth = 2;
                if (isActive) {
                    ctx.shadowColor = COLORS.tcell;
                    ctx.shadowBlur = 10;
                }
                ctx.strokeRect(buttonX, buttonY, buttonWidth, buttonHeight);
                ctx.shadowBlur = 0;

                ctx.fillStyle = COLORS.text;
                ctx.font = '11px Arial';
                ctx.textAlign = 'center';
                const label = speed === 1 ? '1x' : `${speed}x`;
                ctx.fillText(label, buttonX + buttonWidth / 2, buttonY + buttonHeight / 2 + 4);
            });

            ctx.textAlign = 'left';
        }

        // 绘制图例
        function drawLegend() {
            const legendX = scale.width * 0.78;
            const legendY = scale.height * 0.8;

            const items = [
                { color: COLORS.antigen, text: '抗原（病原体）' },
                { color: COLORS.antibody, text: '抗体' },
                { color: COLORS.phagocyte, text: '吞噬细胞' }
            ];

            items.forEach((item, i) => {
                const y = legendY + i * 22;
                ctx.fillStyle = item.color;
                ctx.beginPath();
                ctx.arc(legendX, y, 6, 0, Math.PI * 2);
                ctx.fill();

                ctx.fillStyle = COLORS.text;
                ctx.font = '12px Arial';
                ctx.textAlign = 'left';
                ctx.fillText(item.text, legendX + 15, y + 4);
            });
        }

        // 主更新
        let lastTime = 0;
        function update(currentTime) {
            const dt = Math.min((currentTime - lastTime) / 1000, 0.1);
            lastTime = currentTime;

            playbackSpeed = speedOptions[currentSpeedIndex];

            const smoothFactor = 0.2;
            displayImmuneStrength = displayImmuneStrength * (1 - smoothFactor) + immuneStrength * smoothFactor;

            time += dt * playbackSpeed;

            // 自动生成抗原
            autoGenerateAntigens(dt);

            // 更新所有实体
            antigens.forEach(ag => ag.update(dt * playbackSpeed));
            antibodies.forEach(ab => ab.update(dt * playbackSpeed));
            phagocytes.forEach(ph => ph.update(dt * playbackSpeed));
            tcells.forEach(tc => tc.update(dt * playbackSpeed));
            bcells.forEach(bc => bc.update(dt * playbackSpeed));

            // 清除死亡抗原
            for (let i = antigens.length - 1; i >= 0; i--) {
                if (antigens[i].health <= 0) {
                    antigens.splice(i, 1);
                }
            }

            // 渲染
            ctx.fillStyle = COLORS.background;
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            drawBackgroundGrid();

            phagocytes.forEach(ph => ph.draw());
            tcells.forEach(tc => tc.draw());
            bcells.forEach(bc => bc.draw());
            antigens.forEach(ag => ag.draw());
            antibodies.forEach(ab => ab.draw());

            drawControlPanel();
            drawSpeedControl();
            drawLegend();

            requestAnimationFrame(update);
        }

        // 交互
        canvas.addEventListener('mousedown', (e) => {
            const rect = canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const panelX = scale.width * 0.02;
            const panelY = scale.height * 0.02;
            const panelWidth = scale.width * 0.22;

            const sliderY = panelY + 60 + 5 * 25 + 40;
            const sliderWidth = panelWidth - 30;
            const sliderX = panelX + 15;

            if (x >= sliderX && x <= sliderX + sliderWidth &&
                y >= sliderY - 10 && y <= sliderY + 10) {
                isDragging = true;
            } else {
                const speedPanelY = scale.height * 0.45;
                const buttonWidth = 42;
                const buttonHeight = 28;
                const buttonSpacing = 5;
                const startX = panelX + 15;
                const buttonY = speedPanelY + 40;

                let clicked = false;
                speedOptions.forEach((speed, index) => {
                    const buttonX = startX + index * (buttonWidth + buttonSpacing);
                    if (x >= buttonX && x <= buttonX + buttonWidth &&
                        y >= buttonY && y <= buttonY + buttonHeight) {
                        currentSpeedIndex = index;
                        clicked = true;
                    }
                });

                if (!clicked && x > scale.width * 0.25 && antigens.length < MAX_ANTIGENS) {
                    antigens.push(new Antigen());
                }
            }
        });

        canvas.addEventListener('mousemove', (e) => {
            if (isDragging) {
                const rect = canvas.getBoundingClientRect();
                const x = e.clientX - rect.left;

                const panelX = scale.width * 0.02;
                const panelWidth = scale.width * 0.22;
                const sliderWidth = panelWidth - 30;
                const sliderX = panelX + 15;

                const progress = Math.max(0, Math.min(1, (x - sliderX) / sliderWidth));
                immuneStrength = progress * 100;
            }
        });

        canvas.addEventListener('mouseup', () => {
            isDragging = false;
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'a' || e.key === 'A') {
                if (antigens.length < MAX_ANTIGENS) {
                    antigens.push(new Antigen());
                }
            }
        });

        // 启动
        init();
        requestAnimationFrame(update);

        console.log('免疫应答过程模拟器已启动');
        console.log('- 点击右侧：添加抗原');
        console.log('- 拖拽滑块：调整免疫强度');
        console.log('- A键：添加抗原');
        console.log('- 点击速度按钮：切换播放速度');
    </script>
</body>
</html>
$HTML$,
 75,
 171,
 801,
 false,
 0,
 NOW(),
 '{"name": "免疫应答", "description": "免疫系统对病原体的识别和清除过程", "difficulty": "hard", "render_mode": "html"}');


-- [12/24] 神经信号传导 (medicine, 75分)
INSERT INTO simulator_templates
(subject, topic, code, quality_score, visual_elements, line_count, has_setup_update, variable_count, created_at, metadata)
VALUES
('medicine',
 '神经信号传导',
 $HTML$<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>神经信号传导 - 医学模拟器</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background: #1E293B;
            font-family: 'Arial', sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        #canvas {
            border: 2px solid #334155;
            box-shadow: 0 0 20px rgba(220, 38, 38, 0.3);
            cursor: pointer;
        }
    </style>
</head>
<body>
    <canvas id="canvas" width="1400" height="800"></canvas>

    <script>
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');

        const COLORS = {
            depolarization: '#DC2626',
            repolarization: '#2563EB',
            resting: '#10B981',
            hyperpolarization: '#0EA5E9',
            background: '#1E293B',
            text: '#F1F5F9'
        };

        // 状态
        let time = 0;
        let stimulusStrength = 50;
        let ionConcentration = 100;
        let conductionSpeed = 100;
        let phase = 0; // 0=静息, 1=去极化, 2=复极化, 3=超极化
        let phaseProgress = 0;
        let wavePosition = 0;

        let dragging = null; // null, 'stim', 'ion', 'speed'

        const history = [];
        const MAX_HISTORY = 200;

        // 粒子系统
        const ionParticles = [];
        const neurotransmitters = [];

        class Particle {
            constructor(x, y, color) {
                this.x = x;
                this.y = y;
                this.vx = (Math.random() - 0.5) * 80;
                this.vy = (Math.random() - 0.5) * 80;
                this.life = 1;
                this.color = color;
                this.size = 3 + Math.random() * 3;
            }
            update(dt) {
                this.x += this.vx * dt;
                this.y += this.vy * dt;
                this.life -= dt * 2;
            }
            draw() {
                if (this.life <= 0) return;
                ctx.globalAlpha = this.life;
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
                ctx.globalAlpha = 1;
            }
        }

        // 计算电压
        function getVoltage() {
            const peak = 40 * (ionConcentration / 100);
            if (phase === 0) return -70;
            if (phase === 1) {
                const t = phaseProgress;
                return -70 + (peak + 70) * t;
            }
            if (phase === 2) {
                const t = phaseProgress;
                return peak - (peak + 70) * t;
            }
            if (phase === 3) {
                const t = phaseProgress;
                if (t < 0.5) return -70 - 10 * t * 2;
                else return -80 + 10 * (t - 0.5) * 2;
            }
            return -70;
        }

        // 更新物理
        function updatePhysics(dt) {
            if (phase > 0) {
                phaseProgress += dt * 5;
                if (phaseProgress >= 1) {
                    phaseProgress = 0;
                    phase++;
                    if (phase === 1) {
                        // 去极化开始，产生Na+粒子
                        for (let i = 0; i < 12; i++) {
                            ionParticles.push(new Particle(420, 400, COLORS.depolarization));
                        }
                    }
                    if (phase === 2) {
                        wavePosition = 0;
                        // 复极化开始，产生K+粒子
                        for (let i = 0; i < 12; i++) {
                            ionParticles.push(new Particle(420, 400, COLORS.repolarization));
                        }
                    }
                    if (phase === 3) {
                        // 超极化开始
                        for (let i = 0; i < 8; i++) {
                            ionParticles.push(new Particle(420, 400, COLORS.hyperpolarization));
                        }
                    }
                    if (phase > 3) {
                        phase = 0;
                        // 释放神经递质
                        const synapseX = 960;
                        for (let i = 0; i < Math.round(15 * ionConcentration / 100); i++) {
                            const nt = new Particle(synapseX, 400, '#F59E0B');
                            nt.vx = 50 + Math.random() * 30;
                            nt.vy = (Math.random() - 0.5) * 40;
                            neurotransmitters.push(nt);
                        }
                    }
                }
                if (phase === 1 || phase === 2) {
                    wavePosition += dt * (0.1 + 0.4 * conductionSpeed / 100);
                    if (wavePosition > 1) wavePosition = 1;
                }
            }

            // 更新粒子
            ionParticles.forEach(p => p.update(dt));
            for (let i = ionParticles.length - 1; i >= 0; i--) {
                if (ionParticles[i].life <= 0) ionParticles.splice(i, 1);
            }
            neurotransmitters.forEach(p => p.update(dt));
            for (let i = neurotransmitters.length - 1; i >= 0; i--) {
                if (neurotransmitters[i].life <= 0) neurotransmitters.splice(i, 1);
            }
        }

        // 绘制
        function draw() {
            // 背景
            ctx.fillStyle = COLORS.background;
            ctx.fillRect(0, 0, 1400, 800);

            // 神经元 (中心420, 400)
            const nx = 420, ny = 400, nr = 50;

            // 发光效果
            if (phase === 1) {
                const pulse = 0.5 + 0.5 * Math.sin(time * 20);
                const grad = ctx.createRadialGradient(nx, ny, nr, nx, ny, nr * (3 + pulse));
                grad.addColorStop(0, COLORS.depolarization + 'FF');
                grad.addColorStop(0.5, COLORS.depolarization + '66');
                grad.addColorStop(1, COLORS.depolarization + '00');
                ctx.fillStyle = grad;
                ctx.fillRect(nx - nr * 4, ny - nr * 4, nr * 8, nr * 8);
            } else if (phase === 2) {
                const pulse = 0.5 + 0.5 * Math.sin(time * 15);
                const grad = ctx.createRadialGradient(nx, ny, nr, nx, ny, nr * (2.5 + pulse * 0.5));
                grad.addColorStop(0, COLORS.repolarization + 'FF');
                grad.addColorStop(0.5, COLORS.repolarization + '66');
                grad.addColorStop(1, COLORS.repolarization + '00');
                ctx.fillStyle = grad;
                ctx.fillRect(nx - nr * 3, ny - nr * 3, nr * 6, nr * 6);
            } else if (phase === 3) {
                const pulse = 0.5 + 0.5 * Math.sin(time * 10);
                const grad = ctx.createRadialGradient(nx, ny, nr, nx, ny, nr * (2 + pulse * 0.3));
                grad.addColorStop(0, COLORS.hyperpolarization + 'AA');
                grad.addColorStop(0.5, COLORS.hyperpolarization + '44');
                grad.addColorStop(1, COLORS.hyperpolarization + '00');
                ctx.fillStyle = grad;
                ctx.fillRect(nx - nr * 2.5, ny - nr * 2.5, nr * 5, nr * 5);
            }

            // 神经元体
            let neuronColor = COLORS.resting;
            if (phase === 1) neuronColor = COLORS.depolarization;
            if (phase === 2) neuronColor = COLORS.repolarization;
            if (phase === 3) neuronColor = COLORS.hyperpolarization;

            // 绘制树突（在神经元体之前）
            ctx.strokeStyle = COLORS.resting;
            ctx.lineWidth = 3;
            for (let i = 0; i < 6; i++) {
                const angle = (i / 6) * Math.PI * 2 - Math.PI / 2;
                if (Math.abs(angle) < Math.PI / 3) continue; // 跳过右侧
                const startX = nx + Math.cos(angle) * nr;
                const startY = ny + Math.sin(angle) * nr;
                for (let j = 0; j < 3; j++) {
                    const branchAngle = angle + (j - 1) * 0.3;
                    const len = 30 + j * 15;
                    const endX = startX + Math.cos(branchAngle) * len;
                    const endY = startY + Math.sin(branchAngle) * len;
                    ctx.beginPath();
                    ctx.moveTo(startX, startY);
                    ctx.lineTo(endX, endY);
                    ctx.stroke();
                }
            }

            // 神经元体
            ctx.fillStyle = neuronColor;
            ctx.beginPath();
            ctx.arc(nx, ny, nr, 0, Math.PI * 2);
            ctx.fill();
            ctx.strokeStyle = COLORS.text;
            ctx.lineWidth = 3;
            ctx.stroke();

            // 细胞核
            ctx.fillStyle = 'rgba(241, 245, 249, 0.4)';
            ctx.beginPath();
            ctx.arc(nx, ny, nr * 0.5, 0, Math.PI * 2);
            ctx.fill();

            // 标签
            ctx.fillStyle = COLORS.text;
            ctx.font = 'bold 14px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('神经元细胞体', nx, ny + nr + 20);

            // 轴突
            const axonStart = nx + nr;
            const axonEnd = axonStart + 490;
            ctx.strokeStyle = COLORS.resting;
            ctx.lineWidth = 10;
            ctx.beginPath();
            ctx.moveTo(axonStart, ny);
            ctx.lineTo(axonEnd, ny);
            ctx.stroke();

            // 髓鞘
            for (let i = 0; i < 8; i++) {
                const sx = axonStart + i * 60;
                const alpha = Math.floor(60 * conductionSpeed / 100);
                ctx.fillStyle = `rgba(241, 245, 249, ${alpha / 255})`;
                ctx.fillRect(sx, ny - 15, 50, 30);
                ctx.strokeStyle = `rgba(241, 245, 249, ${alpha / 255})`;
                ctx.lineWidth = 1;
                ctx.strokeRect(sx, ny - 15, 50, 30);
            }

            // 轴突标签
            ctx.fillStyle = COLORS.text;
            ctx.font = '12px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('轴突（有髓鞘）', (axonStart + axonEnd) / 2, ny - 30);

            // 传播波
            if (wavePosition > 0 && wavePosition < 1) {
                const wx = axonStart + 490 * wavePosition;
                const pulse = 0.5 + 0.5 * Math.sin(time * 15);

                const grad = ctx.createRadialGradient(wx, ny, 0, wx, ny, 50);
                grad.addColorStop(0, COLORS.depolarization + 'FF');
                grad.addColorStop(0.5, COLORS.depolarization + '88');
                grad.addColorStop(1, COLORS.depolarization + '00');
                ctx.fillStyle = grad;
                ctx.fillRect(wx - 50, ny - 50, 100, 100);

                ctx.fillStyle = COLORS.depolarization;
                ctx.shadowColor = COLORS.depolarization;
                ctx.shadowBlur = 25;
                ctx.beginPath();
                ctx.arc(wx, ny, 12 + pulse * 6, 0, Math.PI * 2);
                ctx.fill();
                ctx.shadowBlur = 0;
            }

            // 突触结构
            const synapseX = axonEnd;
            const synapseY = ny;

            // 突触前膜
            ctx.fillStyle = '#8B5CF6';
            ctx.strokeStyle = COLORS.text;
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.arc(synapseX, synapseY, 20, 0, Math.PI * 2);
            ctx.fill();
            ctx.stroke();

            // 突触囊泡
            for (let i = 0; i < 5; i++) {
                const angle = (i / 5) * Math.PI * 2;
                const vx = synapseX + Math.cos(angle) * 8;
                const vy = synapseY + Math.sin(angle) * 8;
                ctx.fillStyle = '#F59E0B';
                ctx.beginPath();
                ctx.arc(vx, vy, 4, 0, Math.PI * 2);
                ctx.fill();
            }

            // 突触间隙
            ctx.strokeStyle = 'rgba(241, 245, 249, 0.3)';
            ctx.lineWidth = 2;
            ctx.setLineDash([5, 5]);
            ctx.beginPath();
            ctx.moveTo(synapseX + 20, synapseY - 30);
            ctx.lineTo(synapseX + 20, synapseY + 30);
            ctx.moveTo(synapseX + 50, synapseY - 30);
            ctx.lineTo(synapseX + 50, synapseY + 30);
            ctx.stroke();
            ctx.setLineDash([]);

            // 突触后膜
            ctx.fillStyle = 'rgba(16, 185, 129, 0.5)';
            ctx.strokeStyle = COLORS.text;
            ctx.lineWidth = 2;
            ctx.fillRect(synapseX + 50, synapseY - 40, 15, 80);
            ctx.strokeRect(synapseX + 50, synapseY - 40, 15, 80);

            // 受体
            for (let i = 0; i < 6; i++) {
                ctx.fillStyle = '#2563EB';
                ctx.beginPath();
                ctx.arc(synapseX + 50, synapseY - 30 + i * 12, 5, 0, Math.PI * 2);
                ctx.fill();
            }

            // 突触标签
            ctx.fillStyle = COLORS.text;
            ctx.font = '12px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('突触间隙', synapseX + 35, synapseY + 60);

            // 离子通道
            const channels = [
                { x: nx + 130, y: ny - 80, type: 'Na+', open: phase === 1 },
                { x: nx + 230, y: ny - 80, type: 'K+', open: phase === 2 || phase === 3 }
            ];

            channels.forEach(ch => {
                const size = 30;
                ctx.fillStyle = ch.open ? 'rgba(220, 38, 38, 0.4)' : 'rgba(16, 185, 129, 0.3)';
                ctx.strokeStyle = COLORS.text;
                ctx.lineWidth = 2;
                ctx.fillRect(ch.x - size/2, ch.y - size/2, size, size);
                ctx.strokeRect(ch.x - size/2, ch.y - size/2, size, size);

                if (ch.open) {
                    // 开放状态：门在两侧
                    ctx.fillStyle = COLORS.text;
                    ctx.fillRect(ch.x - size/2, ch.y - size/2, 5, size);
                    ctx.fillRect(ch.x + size/2 - 5, ch.y - size/2, 5, size);

                    // 离子流动
                    for (let i = 0; i < 3; i++) {
                        const iy = ch.y - size/2 + 10 + i * 10 + (time * 50) % 10;
                        ctx.fillStyle = ch.type === 'Na+' ? COLORS.depolarization : COLORS.repolarization;
                        ctx.beginPath();
                        ctx.arc(ch.x, iy, 3, 0, Math.PI * 2);
                        ctx.fill();
                    }
                } else {
                    // 关闭状态：门在中间
                    ctx.fillStyle = COLORS.text;
                    ctx.fillRect(ch.x - size/2, ch.y - 2, size, 4);
                }

                ctx.fillStyle = COLORS.text;
                ctx.font = 'bold 12px Arial';
                ctx.textAlign = 'center';
                ctx.fillText(ch.type, ch.x, ch.y + size/2 + 15);
                ctx.font = '10px Arial';
                ctx.fillText(ch.open ? '开放' : '关闭', ch.x, ch.y + size/2 + 28);
            });

            // 绘制粒子
            ionParticles.forEach(p => p.draw());
            neurotransmitters.forEach(p => p.draw());

            // 电压图 (1050, 400)
            const gx = 1050, gy = 400, gw = 300, gh = 250;

            ctx.fillStyle = 'rgba(30, 41, 59, 0.95)';
            ctx.strokeStyle = COLORS.resting;
            ctx.lineWidth = 2;
            ctx.strokeRect(gx, gy - gh / 2, gw, gh);
            ctx.fillRect(gx, gy - gh / 2, gw, gh);

            ctx.fillStyle = COLORS.text;
            ctx.font = 'bold 16px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('膜电位 (mV)', gx + gw / 2, gy - gh / 2 - 10);

            // 绘制历史曲线
            if (history.length > 1) {
                ctx.strokeStyle = COLORS.depolarization;
                ctx.lineWidth = 2;
                ctx.beginPath();
                for (let i = 0; i < history.length; i++) {
                    const v = history[i];
                    const px = gx + (i / MAX_HISTORY) * gw;
                    const py = gy + gh / 2 - ((v + 90) / 140) * gh;
                    if (i === 0) ctx.moveTo(px, py);
                    else ctx.lineTo(px, py);
                }
                ctx.stroke();
            }

            // 当前电压
            const cv = getVoltage();
            ctx.fillStyle = COLORS.text;
            ctx.font = 'bold 24px Arial';
            ctx.fillText(`${cv.toFixed(1)} mV`, gx + gw / 2, gy + gh / 2 + 35);

            // 刺激按钮 (70, 600)
            const bx = 100, by = 620, br = 30;

            ctx.fillStyle = COLORS.depolarization;
            ctx.beginPath();
            ctx.arc(bx, by, br, 0, Math.PI * 2);
            ctx.fill();
            ctx.strokeStyle = COLORS.text;
            ctx.lineWidth = 3;
            ctx.stroke();

            ctx.fillStyle = COLORS.text;
            ctx.font = 'bold 16px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('刺激', bx, by + 6);

            // 刺激强度滑块 (70, 680)
            ctx.fillStyle = COLORS.text;
            ctx.font = '14px Arial';
            ctx.textAlign = 'left';
            ctx.fillText(`刺激强度: ${Math.round(stimulusStrength)}%`, 50, 670);
            drawSlider(50, 690, 250, stimulusStrength, COLORS.depolarization);

            // 阈值线
            const tx = 50 + 250 * 0.3;
            ctx.strokeStyle = COLORS.text + '80';
            ctx.lineWidth = 2;
            ctx.setLineDash([3, 3]);
            ctx.beginPath();
            ctx.moveTo(tx, 685);
            ctx.lineTo(tx, 695);
            ctx.stroke();
            ctx.setLineDash([]);
            ctx.font = '11px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('阈值30%', tx, 682);

            // Na+浓度 (70, 100)
            ctx.textAlign = 'left';
            ctx.font = '14px Arial';
            ctx.fillText(`Na⁺浓度: ${Math.round(ionConcentration)}%`, 50, 90);
            drawSlider(50, 110, 250, ionConcentration, COLORS.depolarization);
            ctx.font = '11px Arial';
            ctx.fillStyle = COLORS.text + 'AA';
            ctx.fillText('影响电位峰值高度', 50, 128);

            // 传导速度 (70, 200)
            ctx.fillStyle = COLORS.text;
            ctx.font = '14px Arial';
            ctx.fillText(`传导速度: ${Math.round(conductionSpeed)}%`, 50, 180);
            drawSlider(50, 200, 250, conductionSpeed, COLORS.resting);
            ctx.font = '11px Arial';
            ctx.fillStyle = COLORS.text + 'AA';
            ctx.fillText('髓鞘影响信号传导速度', 50, 218);

            // 阶段指示 (1050, 150)
            const phases = ['静息', '去极化', '复极化', '超极化'];
            const colors = [COLORS.resting, COLORS.depolarization, COLORS.repolarization, COLORS.hyperpolarization];

            ctx.fillStyle = COLORS.text;
            ctx.font = 'bold 16px Arial';
            ctx.textAlign = 'left';
            ctx.fillText('动作电位阶段:', 1050, 110);

            for (let i = 0; i < 4; i++) {
                const py = 140 + i * 35;
                const isActive = phase === i;

                ctx.fillStyle = isActive ? colors[i] : colors[i] + '40';

                if (isActive) {
                    const pulse = 0.7 + 0.3 * Math.sin(time * 10);
                    ctx.shadowColor = colors[i];
                    ctx.shadowBlur = 20 * pulse;
                }

                ctx.beginPath();
                ctx.arc(1070, py, isActive ? 12 : 9, 0, Math.PI * 2);
                ctx.fill();
                ctx.shadowBlur = 0;

                if (isActive) {
                    ctx.strokeStyle = COLORS.text;
                    ctx.lineWidth = 2;
                    ctx.stroke();
                }

                ctx.fillStyle = isActive ? COLORS.text : COLORS.text + '80';
                ctx.font = isActive ? 'bold 14px Arial' : '13px Arial';
                ctx.fillText(phases[i], 1095, py + 5);
            }
        }

        // 绘制滑块
        function drawSlider(x, y, w, value, color) {
            // 轨道
            ctx.strokeStyle = '#334155';
            ctx.lineWidth = 5;
            ctx.lineCap = 'round';
            ctx.beginPath();
            ctx.moveTo(x, y);
            ctx.lineTo(x + w, y);
            ctx.stroke();

            // 进度
            const p = value / 100;
            ctx.strokeStyle = color;
            ctx.lineWidth = 5;
            ctx.beginPath();
            ctx.moveTo(x, y);
            ctx.lineTo(x + w * p, y);
            ctx.stroke();

            // 手柄
            ctx.fillStyle = color;
            ctx.shadowColor = color;
            ctx.shadowBlur = 20;
            ctx.beginPath();
            ctx.arc(x + w * p, y, 10, 0, Math.PI * 2);
            ctx.fill();
            ctx.shadowBlur = 0;
        }

        // 主循环
        let lastTime = 0;
        function loop(now) {
            const dt = Math.min((now - lastTime) / 1000, 0.05);
            lastTime = now;

            time += dt;
            updatePhysics(dt);

            history.push(getVoltage());
            if (history.length > MAX_HISTORY) history.shift();

            draw();
            requestAnimationFrame(loop);
        }

        // 鼠标事件
        canvas.addEventListener('mousedown', (e) => {
            const rect = canvas.getBoundingClientRect();
            const mx = e.clientX - rect.left;
            const my = e.clientY - rect.top;

            console.log('点击位置:', mx, my);

            // 刺激按钮 (100, 620, 半径30)
            const dx = mx - 100;
            const dy = my - 620;
            if (dx * dx + dy * dy < 900) { // 30*30
                console.log('触发刺激');
                if (phase === 0 && stimulusStrength >= 30) {
                    phase = 1;
                    phaseProgress = 0;
                    wavePosition = 0;
                }
                return;
            }

            // 刺激滑块 (50-300, 690, ±40像素)
            if (mx >= 50 && mx <= 300 && my >= 650 && my <= 730) {
                console.log('拖动刺激滑块');
                dragging = 'stim';
                stimulusStrength = Math.max(0, Math.min(100, ((mx - 50) / 250) * 100));
                return;
            }

            // Na+滑块 (50-300, 110, ±40像素)
            if (mx >= 50 && mx <= 300 && my >= 70 && my <= 150) {
                console.log('拖动Na+滑块');
                dragging = 'ion';
                ionConcentration = Math.max(0, Math.min(100, ((mx - 50) / 250) * 100));
                return;
            }

            // 速度滑块 (50-300, 200, ±40像素)
            if (mx >= 50 && mx <= 300 && my >= 160 && my <= 240) {
                console.log('拖动速度滑块');
                dragging = 'speed';
                conductionSpeed = Math.max(0, Math.min(100, ((mx - 50) / 250) * 100));
                return;
            }
        });

        canvas.addEventListener('mousemove', (e) => {
            if (dragging) {
                const rect = canvas.getBoundingClientRect();
                const mx = e.clientX - rect.left;
                const v = Math.max(0, Math.min(100, ((mx - 50) / 250) * 100));

                if (dragging === 'stim') stimulusStrength = v;
                else if (dragging === 'ion') ionConcentration = v;
                else if (dragging === 'speed') conductionSpeed = v;
            }
        });

        canvas.addEventListener('mouseup', () => {
            dragging = null;
        });

        // 键盘
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                if (phase === 0 && stimulusStrength >= 30) {
                    phase = 1;
                    phaseProgress = 0;
                    wavePosition = 0;
                }
            }
        });

        requestAnimationFrame(loop);

        console.log('神经信号传导模拟器已启动');
        console.log('- 点击红色圆形按钮触发动作电位');
        console.log('- 拖拽三个滑块调整参数');
        console.log('- 按Enter或空格也可触发');
    </script>
</body>
</html>$HTML$,
 75,
 210,
 648,
 false,
 0,
 NOW(),
 '{"name": "神经信号传导", "description": "神经元之间的电信号和化学信号传递过程", "difficulty": "hard", "render_mode": "html"}');


-- [13/24] 二叉树遍历 (computer_science, 75分)
INSERT INTO simulator_templates
(subject, topic, code, quality_score, visual_elements, line_count, has_setup_update, variable_count, created_at, metadata)
VALUES
('computer_science',
 '二叉树遍历',
 $HTML$<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>二叉树可视化 - 计算机科学</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
            color: #F1F5F9;
            padding: 20px;
            min-height: 100vh;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        h1 {
            text-align: center;
            color: #06B6D4;
            margin-bottom: 10px;
            font-size: 2em;
            text-shadow: 0 0 20px rgba(6, 182, 212, 0.5);
        }

        .subtitle {
            text-align: center;
            color: #94A3B8;
            margin-bottom: 30px;
            font-size: 1.1em;
        }

        .main-grid {
            display: grid;
            grid-template-columns: 300px 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }

        .controls {
            background: rgba(30, 41, 59, 0.6);
            border: 2px solid #334155;
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            height: fit-content;
        }

        .control-section {
            margin-bottom: 25px;
            padding-bottom: 25px;
            border-bottom: 1px solid #334155;
        }

        .control-section:last-child {
            margin-bottom: 0;
            padding-bottom: 0;
            border-bottom: none;
        }

        .control-section h3 {
            color: #8B5CF6;
            margin-bottom: 15px;
            font-size: 1.1em;
        }

        .input-group {
            margin-bottom: 15px;
        }

        .input-group label {
            display: block;
            color: #CBD5E1;
            margin-bottom: 8px;
            font-size: 14px;
        }

        input[type="number"] {
            width: 100%;
            background: #0F172A;
            color: #F1F5F9;
            border: 2px solid #475569;
            border-radius: 8px;
            padding: 10px;
            font-size: 16px;
            transition: all 0.3s;
        }

        input[type="number"]:focus {
            outline: none;
            border-color: #06B6D4;
            box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.1);
        }

        button {
            width: 100%;
            background: linear-gradient(135deg, #06B6D4 0%, #0891B2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 12px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(6, 182, 212, 0.4);
            margin-bottom: 10px;
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(6, 182, 212, 0.6);
        }

        button:active {
            transform: translateY(0);
        }

        button:disabled {
            background: #475569;
            cursor: not-allowed;
            box-shadow: none;
            transform: none;
        }

        .btn-danger {
            background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
            box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4);
        }

        .btn-danger:hover {
            box-shadow: 0 6px 20px rgba(239, 68, 68, 0.6);
        }

        .btn-secondary {
            background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
            box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4);
        }

        .btn-secondary:hover {
            box-shadow: 0 6px 20px rgba(139, 92, 246, 0.6);
        }

        .btn-success {
            background: linear-gradient(135deg, #10B981 0%, #059669 100%);
            box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
        }

        .btn-success:hover {
            box-shadow: 0 6px 20px rgba(16, 185, 129, 0.6);
        }

        .traversal-buttons button {
            margin-bottom: 8px;
        }

        .visualization {
            background: rgba(30, 41, 59, 0.6);
            border: 2px solid #334155;
            border-radius: 15px;
            padding: 30px;
            backdrop-filter: blur(10px);
            min-height: 600px;
            position: relative;
        }

        #treeCanvas {
            width: 100%;
            height: 600px;
            cursor: grab;
        }

        #treeCanvas:active {
            cursor: grabbing;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: rgba(30, 41, 59, 0.6);
            border: 2px solid #334155;
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            text-align: center;
        }

        .stat-label {
            color: #94A3B8;
            font-size: 14px;
            margin-bottom: 8px;
        }

        .stat-value {
            color: #06B6D4;
            font-size: 28px;
            font-weight: bold;
        }

        .traversal-output {
            background: rgba(30, 41, 59, 0.6);
            border: 2px solid #334155;
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(10px);
        }

        .traversal-output h2 {
            color: #8B5CF6;
            margin-bottom: 15px;
            font-size: 1.5em;
        }

        .output-item {
            background: rgba(15, 23, 42, 0.5);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            border-left: 4px solid #06B6D4;
        }

        .output-item h3 {
            color: #06B6D4;
            font-size: 14px;
            margin-bottom: 8px;
        }

        .output-item .values {
            color: #F1F5F9;
            font-family: 'Courier New', monospace;
            font-size: 16px;
            font-weight: bold;
            letter-spacing: 2px;
        }

        .output-item .description {
            color: #94A3B8;
            font-size: 12px;
            margin-top: 8px;
            line-height: 1.5;
        }

        .status-message {
            background: rgba(16, 185, 129, 0.1);
            border: 2px solid #10B981;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            text-align: center;
            color: #10B981;
            font-weight: 600;
            display: none;
        }

        .status-message.show {
            display: block;
            animation: fadeIn 0.3s;
        }

        .status-message.error {
            background: rgba(239, 68, 68, 0.1);
            border-color: #EF4444;
            color: #EF4444;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .legend {
            display: flex;
            gap: 15px;
            justify-content: center;
            flex-wrap: wrap;
            padding: 15px;
            background: rgba(15, 23, 42, 0.5);
            border-radius: 10px;
            margin-top: 15px;
        }

        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
        }

        .legend-color {
            width: 16px;
            height: 16px;
            border-radius: 50%;
        }

        @media (max-width: 1024px) {
            .main-grid {
                grid-template-columns: 1fr;
            }

            .controls {
                max-width: 600px;
                margin: 0 auto 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌳 二叉树可视化</h1>
        <p class="subtitle">探索二叉搜索树的结构与遍历算法</p>

        <div class="status-message" id="statusMessage"></div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-label">节点总数</div>
                <div class="stat-value" id="nodeCount">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">树的高度</div>
                <div class="stat-value" id="treeHeight">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">叶子节点</div>
                <div class="stat-value" id="leafCount">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">最小值</div>
                <div class="stat-value" id="minValue">-</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">最大值</div>
                <div class="stat-value" id="maxValue">-</div>
            </div>
        </div>

        <div class="main-grid">
            <div class="controls">
                <div class="control-section">
                    <h3>插入节点</h3>
                    <div class="input-group">
                        <label>节点值 (1-99)</label>
                        <input type="number" id="insertValue" min="1" max="99" placeholder="输入数值">
                    </div>
                    <button onclick="insertNode()" class="btn-success">插入节点</button>
                    <button onclick="insertRandom()">随机插入</button>
                    <button onclick="insertMultiple()">批量插入</button>
                </div>

                <div class="control-section">
                    <h3>删除节点</h3>
                    <div class="input-group">
                        <label>节点值</label>
                        <input type="number" id="deleteValue" min="1" max="99" placeholder="输入数值">
                    </div>
                    <button onclick="deleteNode()" class="btn-danger">删除节点</button>
                </div>

                <div class="control-section">
                    <h3>树遍历</h3>
                    <div class="traversal-buttons">
                        <button onclick="traversePreorder()" class="btn-secondary">前序遍历</button>
                        <button onclick="traverseInorder()" class="btn-secondary">中序遍历</button>
                        <button onclick="traversePostorder()" class="btn-secondary">后序遍历</button>
                        <button onclick="traverseLevelorder()" class="btn-secondary">层序遍历</button>
                    </div>
                </div>

                <div class="control-section">
                    <h3>操作</h3>
                    <button onclick="clearTree()" class="btn-danger">清空树</button>
                    <button onclick="balanceTree()">平衡树</button>
                </div>
            </div>

            <div class="visualization">
                <canvas id="treeCanvas"></canvas>
                <div class="legend">
                    <div class="legend-item">
                        <div class="legend-color" style="background: #06B6D4;"></div>
                        <span>普通节点</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #8B5CF6;"></div>
                        <span>根节点</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #10B981;"></div>
                        <span>叶子节点</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #F59E0B;"></div>
                        <span>高亮节点</span>
                    </div>
                </div>
            </div>
        </div>

        <div class="traversal-output">
            <h2>遍历结果</h2>
            <div class="output-item">
                <h3>前序遍历 (Preorder)</h3>
                <div class="values" id="preorderOutput">-</div>
                <div class="description">访问顺序：根节点 → 左子树 → 右子树</div>
            </div>
            <div class="output-item">
                <h3>中序遍历 (Inorder)</h3>
                <div class="values" id="inorderOutput">-</div>
                <div class="description">访问顺序：左子树 → 根节点 → 右子树（升序排列）</div>
            </div>
            <div class="output-item">
                <h3>后序遍历 (Postorder)</h3>
                <div class="values" id="postorderOutput">-</div>
                <div class="description">访问顺序：左子树 → 右子树 → 根节点</div>
            </div>
            <div class="output-item">
                <h3>层序遍历 (Level-order)</h3>
                <div class="values" id="levelorderOutput">-</div>
                <div class="description">访问顺序：从上到下，从左到右逐层遍历</div>
            </div>
        </div>
    </div>

    <script>
        // 树节点类
        class TreeNode {
            constructor(value) {
                this.value = value;
                this.left = null;
                this.right = null;
                this.x = 0;
                this.y = 0;
            }
        }

        // 二叉搜索树
        class BinarySearchTree {
            constructor() {
                this.root = null;
            }

            insert(value) {
                const newNode = new TreeNode(value);
                if (!this.root) {
                    this.root = newNode;
                    return true;
                }

                let current = this.root;
                while (true) {
                    if (value === current.value) return false;

                    if (value < current.value) {
                        if (!current.left) {
                            current.left = newNode;
                            return true;
                        }
                        current = current.left;
                    } else {
                        if (!current.right) {
                            current.right = newNode;
                            return true;
                        }
                        current = current.right;
                    }
                }
            }

            delete(value) {
                this.root = this._deleteNode(this.root, value);
            }

            _deleteNode(node, value) {
                if (!node) return null;

                if (value < node.value) {
                    node.left = this._deleteNode(node.left, value);
                } else if (value > node.value) {
                    node.right = this._deleteNode(node.right, value);
                } else {
                    // 找到要删除的节点
                    if (!node.left && !node.right) return null;
                    if (!node.left) return node.right;
                    if (!node.right) return node.left;

                    // 有两个子节点：找右子树最小值
                    let minRight = node.right;
                    while (minRight.left) {
                        minRight = minRight.left;
                    }
                    node.value = minRight.value;
                    node.right = this._deleteNode(node.right, minRight.value);
                }
                return node;
            }

            preorder(node = this.root, result = []) {
                if (node) {
                    result.push(node.value);
                    this.preorder(node.left, result);
                    this.preorder(node.right, result);
                }
                return result;
            }

            inorder(node = this.root, result = []) {
                if (node) {
                    this.inorder(node.left, result);
                    result.push(node.value);
                    this.inorder(node.right, result);
                }
                return result;
            }

            postorder(node = this.root, result = []) {
                if (node) {
                    this.postorder(node.left, result);
                    this.postorder(node.right, result);
                    result.push(node.value);
                }
                return result;
            }

            levelorder() {
                if (!this.root) return [];
                const result = [];
                const queue = [this.root];

                while (queue.length > 0) {
                    const node = queue.shift();
                    result.push(node.value);
                    if (node.left) queue.push(node.left);
                    if (node.right) queue.push(node.right);
                }
                return result;
            }

            height(node = this.root) {
                if (!node) return 0;
                return 1 + Math.max(this.height(node.left), this.height(node.right));
            }

            countNodes(node = this.root) {
                if (!node) return 0;
                return 1 + this.countNodes(node.left) + this.countNodes(node.right);
            }

            countLeaves(node = this.root) {
                if (!node) return 0;
                if (!node.left && !node.right) return 1;
                return this.countLeaves(node.left) + this.countLeaves(node.right);
            }

            findMin(node = this.root) {
                if (!node) return null;
                while (node.left) node = node.left;
                return node.value;
            }

            findMax(node = this.root) {
                if (!node) return null;
                while (node.right) node = node.right;
                return node.value;
            }
        }

        let tree = new BinarySearchTree();
        let canvas, ctx;
        let highlightedNodes = new Set();
        let animationSpeed = 500;

        // 初始化
        function init() {
            canvas = document.getElementById('treeCanvas');
            ctx = canvas.getContext('2d');
            resizeCanvas();

            window.addEventListener('resize', resizeCanvas);

            // 添加示例数据
            [50, 30, 70, 20, 40, 60, 80].forEach(val => tree.insert(val));
            updateTree();
        }

        function resizeCanvas() {
            const container = canvas.parentElement;
            canvas.width = container.clientWidth - 60;
            canvas.height = 600;
            drawTree();
        }

        // 插入节点
        function insertNode() {
            const value = parseInt(document.getElementById('insertValue').value);
            if (!value || value < 1 || value > 99) {
                showStatus('请输入1-99之间的数值', 'error');
                return;
            }

            if (tree.insert(value)) {
                showStatus(`✓ 成功插入节点 ${value}`);
                document.getElementById('insertValue').value = '';
                updateTree();
            } else {
                showStatus(`节点 ${value} 已存在`, 'error');
            }
        }

        // 随机插入
        function insertRandom() {
            const value = Math.floor(Math.random() * 99) + 1;
            if (tree.insert(value)) {
                showStatus(`✓ 随机插入节点 ${value}`);
                updateTree();
            } else {
                insertRandom(); // 重试
            }
        }

        // 批量插入
        function insertMultiple() {
            const count = 5;
            let inserted = 0;
            for (let i = 0; i < count * 2 && inserted < count; i++) {
                const value = Math.floor(Math.random() * 99) + 1;
                if (tree.insert(value)) inserted++;
            }
            showStatus(`✓ 批量插入了 ${inserted} 个节点`);
            updateTree();
        }

        // 删除节点
        function deleteNode() {
            const value = parseInt(document.getElementById('deleteValue').value);
            if (!value) {
                showStatus('请输入要删除的节点值', 'error');
                return;
            }

            tree.delete(value);
            showStatus(`✓ 已删除节点 ${value}`);
            document.getElementById('deleteValue').value = '';
            updateTree();
        }

        // 清空树
        function clearTree() {
            tree = new BinarySearchTree();
            updateTree();
            showStatus('✓ 已清空树');
        }

        // 平衡树
        function balanceTree() {
            const values = tree.inorder();
            tree = new BinarySearchTree();

            function insertBalanced(arr, start, end) {
                if (start > end) return;
                const mid = Math.floor((start + end) / 2);
                tree.insert(arr[mid]);
                insertBalanced(arr, start, mid - 1);
                insertBalanced(arr, mid + 1, end);
            }

            insertBalanced(values, 0, values.length - 1);
            updateTree();
            showStatus('✓ 树已重新平衡');
        }

        // 遍历动画
        async function traversePreorder() {
            await animateTraversal(tree.preorder(), 'preorder');
        }

        async function traverseInorder() {
            await animateTraversal(tree.inorder(), 'inorder');
        }

        async function traversePostorder() {
            await animateTraversal(tree.postorder(), 'postorder');
        }

        async function traverseLevelorder() {
            await animateTraversal(tree.levelorder(), 'levelorder');
        }

        async function animateTraversal(values, type) {
            if (values.length === 0) {
                showStatus('树为空', 'error');
                return;
            }

            const outputId = type + 'Output';
            document.getElementById(outputId).textContent = '';
            highlightedNodes.clear();

            for (let i = 0; i < values.length; i++) {
                highlightedNodes.add(values[i]);
                drawTree();

                const current = values.slice(0, i + 1).join(' → ');
                document.getElementById(outputId).textContent = current;

                await sleep(animationSpeed);
            }

            showStatus(`✓ ${type.toUpperCase()} 遍历完成`);
        }

        // 更新树
        function updateTree() {
            updateStats();
            updateAllTraversals();
            drawTree();
        }

        // 更新统计
        function updateStats() {
            document.getElementById('nodeCount').textContent = tree.countNodes();
            document.getElementById('treeHeight').textContent = tree.height();
            document.getElementById('leafCount').textContent = tree.countLeaves();
            document.getElementById('minValue').textContent = tree.findMin() || '-';
            document.getElementById('maxValue').textContent = tree.findMax() || '-';
        }

        // 更新所有遍历结果
        function updateAllTraversals() {
            document.getElementById('preorderOutput').textContent =
                tree.preorder().join(' → ') || '-';
            document.getElementById('inorderOutput').textContent =
                tree.inorder().join(' → ') || '-';
            document.getElementById('postorderOutput').textContent =
                tree.postorder().join(' → ') || '-';
            document.getElementById('levelorderOutput').textContent =
                tree.levelorder().join(' → ') || '-';
        }

        // 绘制树
        function drawTree() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            if (!tree.root) {
                ctx.fillStyle = '#94A3B8';
                ctx.font = '18px sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText('树为空 - 插入节点开始构建', canvas.width / 2, canvas.height / 2);
                return;
            }

            calculatePositions();
            drawNode(tree.root, true);
        }

        // 计算节点位置
        function calculatePositions() {
            const height = tree.height();
            const levelHeight = Math.min(80, canvas.height / (height + 1));

            function calculate(node, level, left, right) {
                if (!node) return;

                node.x = (left + right) / 2;
                node.y = (level + 1) * levelHeight;

                const mid = (left + right) / 2;
                calculate(node.left, level + 1, left, mid);
                calculate(node.right, level + 1, mid, right);
            }

            calculate(tree.root, 0, 0, canvas.width);
        }

        // 绘制节点
        function drawNode(node, isRoot = false) {
            if (!node) return;

            // 绘制连接线
            if (node.left) {
                ctx.strokeStyle = '#475569';
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.moveTo(node.x, node.y);
                ctx.lineTo(node.left.x, node.left.y);
                ctx.stroke();
            }
            if (node.right) {
                ctx.strokeStyle = '#475569';
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.moveTo(node.x, node.y);
                ctx.lineTo(node.right.x, node.right.y);
                ctx.stroke();
            }

            // 递归绘制子节点
            drawNode(node.left);
            drawNode(node.right);

            // 绘制节点
            const radius = 25;
            const isLeaf = !node.left && !node.right;
            const isHighlighted = highlightedNodes.has(node.value);

            // 节点颜色
            let gradient = ctx.createRadialGradient(node.x, node.y, 0, node.x, node.y, radius);
            if (isHighlighted) {
                gradient.addColorStop(0, '#FCD34D');
                gradient.addColorStop(1, '#F59E0B');
            } else if (isRoot) {
                gradient.addColorStop(0, '#A78BFA');
                gradient.addColorStop(1, '#8B5CF6');
            } else if (isLeaf) {
                gradient.addColorStop(0, '#34D399');
                gradient.addColorStop(1, '#10B981');
            } else {
                gradient.addColorStop(0, '#22D3EE');
                gradient.addColorStop(1, '#06B6D4');
            }

            // 绘制节点圆圈
            ctx.fillStyle = gradient;
            ctx.beginPath();
            ctx.arc(node.x, node.y, radius, 0, Math.PI * 2);
            ctx.fill();

            // 节点边框
            ctx.strokeStyle = isHighlighted ? '#F59E0B' : 'rgba(255, 255, 255, 0.3)';
            ctx.lineWidth = isHighlighted ? 3 : 2;
            ctx.stroke();

            // 绘制阴影
            if (isHighlighted) {
                ctx.shadowColor = '#F59E0B';
                ctx.shadowBlur = 20;
            }

            // 绘制节点值
            ctx.fillStyle = '#FFFFFF';
            ctx.font = 'bold 16px sans-serif';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.shadowColor = 'transparent';
            ctx.shadowBlur = 0;
            ctx.fillText(node.value, node.x, node.y);
        }

        // 显示状态消息
        function showStatus(message, type = 'success') {
            const statusEl = document.getElementById('statusMessage');
            statusEl.textContent = message;
            statusEl.className = 'status-message show';
            if (type === 'error') statusEl.classList.add('error');
            setTimeout(() => statusEl.classList.remove('show'), 3000);
        }

        // 延迟函数
        function sleep(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        }

        // 回车键监听
        document.getElementById('insertValue').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') insertNode();
        });
        document.getElementById('deleteValue').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') deleteNode();
        });

        // 初始化
        window.addEventListener('load', init);
    </script>
</body>
</html>$HTML$,
 75,
 34,
 887,
 false,
 0,
 NOW(),
 '{"name": "二叉树遍历", "description": "二叉树的前序、中序、后序遍历可视化", "difficulty": "medium", "render_mode": "html"}');


-- [14/24] 排序算法可视化 (computer_science, 75分)
INSERT INTO simulator_templates
(subject, topic, code, quality_score, visual_elements, line_count, has_setup_update, variable_count, created_at, metadata)
VALUES
('computer_science',
 '排序算法可视化',
 $HTML$<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>排序算法可视化 - 计算机科学</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
            color: #F1F5F9;
            padding: 20px;
            min-height: 100vh;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        h1 {
            text-align: center;
            color: #06B6D4;
            margin-bottom: 10px;
            font-size: 2em;
            text-shadow: 0 0 20px rgba(6, 182, 212, 0.5);
        }

        .subtitle {
            text-align: center;
            color: #94A3B8;
            margin-bottom: 30px;
            font-size: 1.1em;
        }

        .controls {
            background: rgba(30, 41, 59, 0.6);
            border: 2px solid #334155;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
        }

        .control-row {
            display: flex;
            gap: 15px;
            align-items: center;
            flex-wrap: wrap;
            margin-bottom: 15px;
        }

        .control-row:last-child {
            margin-bottom: 0;
        }

        label {
            color: #CBD5E1;
            font-weight: 500;
            min-width: 100px;
        }

        select, input[type="range"] {
            background: #0F172A;
            color: #F1F5F9;
            border: 2px solid #475569;
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s;
        }

        select:hover, select:focus {
            border-color: #06B6D4;
            outline: none;
        }

        input[type="range"] {
            flex: 1;
            max-width: 300px;
        }

        .button-group {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }

        button {
            background: linear-gradient(135deg, #06B6D4 0%, #0891B2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 12px 24px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(6, 182, 212, 0.4);
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(6, 182, 212, 0.6);
        }

        button:active {
            transform: translateY(0);
        }

        button:disabled {
            background: #475569;
            cursor: not-allowed;
            box-shadow: none;
            transform: none;
        }

        .btn-secondary {
            background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
            box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4);
        }

        .btn-secondary:hover {
            box-shadow: 0 6px 20px rgba(139, 92, 246, 0.6);
        }

        .btn-success {
            background: linear-gradient(135deg, #10B981 0%, #059669 100%);
            box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
        }

        .btn-success:hover {
            box-shadow: 0 6px 20px rgba(16, 185, 129, 0.6);
        }

        .visualization {
            background: rgba(30, 41, 59, 0.6);
            border: 2px solid #334155;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
            min-height: 400px;
        }

        .bars-container {
            display: flex;
            align-items: flex-end;
            justify-content: center;
            gap: 2px;
            height: 350px;
            padding: 10px;
        }

        .bar {
            flex: 1;
            background: linear-gradient(180deg, #06B6D4 0%, #0891B2 100%);
            border-radius: 4px 4px 0 0;
            transition: all 0.3s;
            position: relative;
            display: flex;
            align-items: flex-end;
            justify-content: center;
            box-shadow: 0 0 10px rgba(6, 182, 212, 0.3);
        }

        .bar.comparing {
            background: linear-gradient(180deg, #F59E0B 0%, #D97706 100%);
            box-shadow: 0 0 20px rgba(245, 158, 11, 0.6);
            transform: scale(1.05);
        }

        .bar.swapping {
            background: linear-gradient(180deg, #EF4444 0%, #DC2626 100%);
            box-shadow: 0 0 20px rgba(239, 68, 68, 0.6);
            transform: scale(1.1);
        }

        .bar.sorted {
            background: linear-gradient(180deg, #10B981 0%, #059669 100%);
            box-shadow: 0 0 15px rgba(16, 185, 129, 0.5);
        }

        .bar.pivot {
            background: linear-gradient(180deg, #8B5CF6 0%, #7C3AED 100%);
            box-shadow: 0 0 20px rgba(139, 92, 246, 0.6);
        }

        .bar-value {
            color: white;
            font-weight: bold;
            font-size: 12px;
            padding: 5px;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: rgba(30, 41, 59, 0.6);
            border: 2px solid #334155;
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            text-align: center;
        }

        .stat-label {
            color: #94A3B8;
            font-size: 14px;
            margin-bottom: 8px;
        }

        .stat-value {
            color: #06B6D4;
            font-size: 28px;
            font-weight: bold;
        }

        .algorithm-info {
            background: rgba(30, 41, 59, 0.6);
            border: 2px solid #334155;
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(10px);
        }

        .algorithm-info h2 {
            color: #8B5CF6;
            margin-bottom: 15px;
            font-size: 1.5em;
        }

        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .info-item {
            background: rgba(15, 23, 42, 0.5);
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #06B6D4;
        }

        .info-item h3 {
            color: #06B6D4;
            font-size: 16px;
            margin-bottom: 8px;
        }

        .info-item p {
            color: #CBD5E1;
            line-height: 1.6;
        }

        .complexity {
            display: inline-block;
            background: rgba(139, 92, 246, 0.2);
            color: #8B5CF6;
            padding: 4px 12px;
            border-radius: 6px;
            font-family: 'Courier New', monospace;
            font-weight: bold;
            margin-top: 8px;
        }

        .status-message {
            background: rgba(16, 185, 129, 0.1);
            border: 2px solid #10B981;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            text-align: center;
            color: #10B981;
            font-weight: 600;
            display: none;
        }

        .status-message.show {
            display: block;
            animation: fadeIn 0.3s;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .legend {
            display: flex;
            gap: 20px;
            justify-content: center;
            flex-wrap: wrap;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #334155;
        }

        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .legend-color {
            width: 30px;
            height: 20px;
            border-radius: 4px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        }

        .legend-color.default {
            background: linear-gradient(180deg, #06B6D4 0%, #0891B2 100%);
        }

        .legend-color.comparing {
            background: linear-gradient(180deg, #F59E0B 0%, #D97706 100%);
        }

        .legend-color.swapping {
            background: linear-gradient(180deg, #EF4444 0%, #DC2626 100%);
        }

        .legend-color.sorted {
            background: linear-gradient(180deg, #10B981 0%, #059669 100%);
        }

        .legend-color.pivot {
            background: linear-gradient(180deg, #8B5CF6 0%, #7C3AED 100%);
        }

        @media (max-width: 768px) {
            .control-row {
                flex-direction: column;
                align-items: stretch;
            }

            label {
                min-width: auto;
            }

            input[type="range"] {
                max-width: 100%;
            }

            .bar-value {
                font-size: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔢 排序算法可视化</h1>
        <p class="subtitle">探索经典排序算法的工作原理与时间复杂度</p>

        <div class="status-message" id="statusMessage"></div>

        <div class="controls">
            <div class="control-row">
                <label>排序算法：</label>
                <select id="algorithmSelect">
                    <option value="bubble">冒泡排序 (Bubble Sort)</option>
                    <option value="quick">快速排序 (Quick Sort)</option>
                    <option value="merge">归并排序 (Merge Sort)</option>
                </select>
            </div>

            <div class="control-row">
                <label>数组大小：</label>
                <input type="range" id="sizeSlider" min="5" max="50" value="15">
                <span id="sizeValue">15</span>
            </div>

            <div class="control-row">
                <label>动画速度：</label>
                <input type="range" id="speedSlider" min="10" max="1000" value="300">
                <span id="speedValue">300ms</span>
            </div>

            <div class="control-row">
                <div class="button-group">
                    <button onclick="generateArray()">生成新数组</button>
                    <button onclick="startSort()" class="btn-success" id="startBtn">开始排序</button>
                    <button onclick="pauseSort()" class="btn-secondary" id="pauseBtn" disabled>暂停</button>
                    <button onclick="resetSort()" id="resetBtn">重置</button>
                </div>
            </div>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-label">比较次数</div>
                <div class="stat-value" id="comparisons">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">交换次数</div>
                <div class="stat-value" id="swaps">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">数组访问次数</div>
                <div class="stat-value" id="accesses">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">执行时间</div>
                <div class="stat-value" id="time">0ms</div>
            </div>
        </div>

        <div class="visualization">
            <div class="bars-container" id="barsContainer"></div>
            <div class="legend">
                <div class="legend-item">
                    <div class="legend-color default"></div>
                    <span>未排序</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color comparing"></div>
                    <span>比较中</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color swapping"></div>
                    <span>交换中</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color pivot"></div>
                    <span>基准值</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color sorted"></div>
                    <span>已排序</span>
                </div>
            </div>
        </div>

        <div class="algorithm-info" id="algorithmInfo">
            <h2>算法信息</h2>
            <div class="info-grid" id="infoGrid"></div>
        </div>
    </div>

    <script>
        let array = [];
        let stats = {
            comparisons: 0,
            swaps: 0,
            accesses: 0,
            startTime: 0
        };
        let isPaused = false;
        let isSorting = false;
        let animationSpeed = 300;
        let sortingSteps = [];
        let currentStep = 0;

        const algorithmData = {
            bubble: {
                name: '冒泡排序',
                description: '重复遍历数组，比较相邻元素并交换，直到数组有序',
                timeComplexity: {
                    best: 'O(n)',
                    average: 'O(n²)',
                    worst: 'O(n²)'
                },
                spaceComplexity: 'O(1)',
                stable: '是',
                features: '简单易懂，适合小规模数据，相邻元素比较交换'
            },
            quick: {
                name: '快速排序',
                description: '选择基准值，将数组分为两部分，递归排序',
                timeComplexity: {
                    best: 'O(n log n)',
                    average: 'O(n log n)',
                    worst: 'O(n²)'
                },
                spaceComplexity: 'O(log n)',
                stable: '否',
                features: '分治策略，实践中最快，不稳定排序'
            },
            merge: {
                name: '归并排序',
                description: '将数组分成两半，递归排序后合并',
                timeComplexity: {
                    best: 'O(n log n)',
                    average: 'O(n log n)',
                    worst: 'O(n log n)'
                },
                spaceComplexity: 'O(n)',
                stable: '是',
                features: '稳定排序，性能稳定，需要额外空间'
            }
        };

        // 初始化
        function init() {
            generateArray();
            updateAlgorithmInfo();

            document.getElementById('algorithmSelect').addEventListener('change', updateAlgorithmInfo);
            document.getElementById('sizeSlider').addEventListener('input', function() {
                document.getElementById('sizeValue').textContent = this.value;
                if (!isSorting) generateArray();
            });
            document.getElementById('speedSlider').addEventListener('input', function() {
                animationSpeed = parseInt(this.value);
                document.getElementById('speedValue').textContent = animationSpeed + 'ms';
            });
        }

        // 生成随机数组
        function generateArray() {
            if (isSorting) return;

            const size = parseInt(document.getElementById('sizeSlider').value);
            array = [];
            for (let i = 0; i < size; i++) {
                array.push(Math.floor(Math.random() * 100) + 10);
            }
            resetStats();
            renderBars();
        }

        // 渲染柱状图
        function renderBars(highlightIndices = {}) {
            const container = document.getElementById('barsContainer');
            container.innerHTML = '';

            const maxValue = Math.max(...array);

            array.forEach((value, index) => {
                const bar = document.createElement('div');
                bar.className = 'bar';
                bar.style.height = `${(value / maxValue) * 300}px`;

                if (highlightIndices.comparing && highlightIndices.comparing.includes(index)) {
                    bar.classList.add('comparing');
                }
                if (highlightIndices.swapping && highlightIndices.swapping.includes(index)) {
                    bar.classList.add('swapping');
                }
                if (highlightIndices.sorted && highlightIndices.sorted.includes(index)) {
                    bar.classList.add('sorted');
                }
                if (highlightIndices.pivot && highlightIndices.pivot.includes(index)) {
                    bar.classList.add('pivot');
                }

                const valueLabel = document.createElement('div');
                valueLabel.className = 'bar-value';
                valueLabel.textContent = value;
                bar.appendChild(valueLabel);

                container.appendChild(bar);
            });
        }

        // 重置统计
        function resetStats() {
            stats = { comparisons: 0, swaps: 0, accesses: 0, startTime: 0 };
            updateStats();
        }

        // 更新统计显示
        function updateStats() {
            document.getElementById('comparisons').textContent = stats.comparisons;
            document.getElementById('swaps').textContent = stats.swaps;
            document.getElementById('accesses').textContent = stats.accesses;

            if (stats.startTime > 0) {
                const elapsed = Date.now() - stats.startTime;
                document.getElementById('time').textContent = elapsed + 'ms';
            }
        }

        // 显示状态消息
        function showStatus(message, duration = 3000) {
            const statusEl = document.getElementById('statusMessage');
            statusEl.textContent = message;
            statusEl.classList.add('show');
            setTimeout(() => statusEl.classList.remove('show'), duration);
        }

        // 延迟函数
        function sleep(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        }

        // 开始排序
        async function startSort() {
            if (isSorting) return;

            isSorting = true;
            isPaused = false;
            stats.startTime = Date.now();

            document.getElementById('startBtn').disabled = true;
            document.getElementById('pauseBtn').disabled = false;
            document.getElementById('resetBtn').disabled = true;
            document.getElementById('algorithmSelect').disabled = true;

            const algorithm = document.getElementById('algorithmSelect').value;

            try {
                switch (algorithm) {
                    case 'bubble':
                        await bubbleSort();
                        break;
                    case 'quick':
                        await quickSort(0, array.length - 1);
                        break;
                    case 'merge':
                        await mergeSort(0, array.length - 1);
                        break;
                }

                // 标记所有为已排序
                renderBars({ sorted: array.map((_, i) => i) });
                showStatus('✓ 排序完成！');
            } catch (error) {
                if (error.message !== 'paused') {
                    console.error('排序错误:', error);
                }
            }

            finishSort();
        }

        // 暂停排序
        function pauseSort() {
            isPaused = true;
            document.getElementById('pauseBtn').disabled = true;
            document.getElementById('startBtn').disabled = false;
            showStatus('⏸ 已暂停');
        }

        // 重置排序
        function resetSort() {
            isSorting = false;
            isPaused = false;
            generateArray();
            finishSort();
            showStatus('↻ 已重置');
        }

        // 完成排序
        function finishSort() {
            isSorting = false;
            document.getElementById('startBtn').disabled = false;
            document.getElementById('pauseBtn').disabled = true;
            document.getElementById('resetBtn').disabled = false;
            document.getElementById('algorithmSelect').disabled = false;
        }

        // 冒泡排序
        async function bubbleSort() {
            const n = array.length;

            for (let i = 0; i < n - 1; i++) {
                let swapped = false;

                for (let j = 0; j < n - i - 1; j++) {
                    if (isPaused) throw new Error('paused');

                    stats.comparisons++;
                    stats.accesses += 2;
                    updateStats();

                    renderBars({ comparing: [j, j + 1] });
                    await sleep(animationSpeed);

                    if (array[j] > array[j + 1]) {
                        stats.swaps++;
                        renderBars({ swapping: [j, j + 1] });
                        await sleep(animationSpeed / 2);

                        [array[j], array[j + 1]] = [array[j + 1], array[j]];
                        swapped = true;

                        renderBars({ swapping: [j, j + 1] });
                        await sleep(animationSpeed / 2);
                    }
                }

                renderBars({ sorted: Array.from({length: i + 1}, (_, k) => n - 1 - k) });

                if (!swapped) break;
            }
        }

        // 快速排序
        async function quickSort(low, high) {
            if (low < high) {
                const pi = await partition(low, high);
                await quickSort(low, pi - 1);
                await quickSort(pi + 1, high);
            }
        }

        async function partition(low, high) {
            const pivot = array[high];
            stats.accesses++;

            renderBars({ pivot: [high] });
            await sleep(animationSpeed);

            let i = low - 1;

            for (let j = low; j < high; j++) {
                if (isPaused) throw new Error('paused');

                stats.comparisons++;
                stats.accesses++;
                updateStats();

                renderBars({ comparing: [j], pivot: [high] });
                await sleep(animationSpeed);

                if (array[j] < pivot) {
                    i++;
                    if (i !== j) {
                        stats.swaps++;
                        renderBars({ swapping: [i, j], pivot: [high] });
                        await sleep(animationSpeed / 2);

                        [array[i], array[j]] = [array[j], array[i]];

                        renderBars({ swapping: [i, j], pivot: [high] });
                        await sleep(animationSpeed / 2);
                    }
                }
            }

            stats.swaps++;
            renderBars({ swapping: [i + 1, high] });
            await sleep(animationSpeed / 2);

            [array[i + 1], array[high]] = [array[high], array[i + 1]];

            renderBars({ swapping: [i + 1, high] });
            await sleep(animationSpeed / 2);

            return i + 1;
        }

        // 归并排序
        async function mergeSort(left, right) {
            if (left < right) {
                const mid = Math.floor((left + right) / 2);

                await mergeSort(left, mid);
                await mergeSort(mid + 1, right);
                await merge(left, mid, right);
            }
        }

        async function merge(left, mid, right) {
            const leftArr = array.slice(left, mid + 1);
            const rightArr = array.slice(mid + 1, right + 1);

            let i = 0, j = 0, k = left;

            while (i < leftArr.length && j < rightArr.length) {
                if (isPaused) throw new Error('paused');

                stats.comparisons++;
                stats.accesses += 2;
                updateStats();

                renderBars({ comparing: [left + i, mid + 1 + j] });
                await sleep(animationSpeed);

                if (leftArr[i] <= rightArr[j]) {
                    array[k] = leftArr[i];
                    i++;
                } else {
                    array[k] = rightArr[j];
                    j++;
                }

                stats.accesses++;
                renderBars({ swapping: [k] });
                await sleep(animationSpeed / 2);

                k++;
            }

            while (i < leftArr.length) {
                if (isPaused) throw new Error('paused');
                array[k] = leftArr[i];
                stats.accesses++;
                renderBars({ swapping: [k] });
                await sleep(animationSpeed / 2);
                i++;
                k++;
            }

            while (j < rightArr.length) {
                if (isPaused) throw new Error('paused');
                array[k] = rightArr[j];
                stats.accesses++;
                renderBars({ swapping: [k] });
                await sleep(animationSpeed / 2);
                j++;
                k++;
            }
        }

        // 更新算法信息
        function updateAlgorithmInfo() {
            const algorithm = document.getElementById('algorithmSelect').value;
            const info = algorithmData[algorithm];

            const infoHTML = `
                <div class="info-item">
                    <h3>算法描述</h3>
                    <p>${info.description}</p>
                </div>
                <div class="info-item">
                    <h3>时间复杂度</h3>
                    <p>最佳: <span class="complexity">${info.timeComplexity.best}</span></p>
                    <p>平均: <span class="complexity">${info.timeComplexity.average}</span></p>
                    <p>最坏: <span class="complexity">${info.timeComplexity.worst}</span></p>
                </div>
                <div class="info-item">
                    <h3>空间复杂度</h3>
                    <p><span class="complexity">${info.spaceComplexity}</span></p>
                </div>
                <div class="info-item">
                    <h3>算法特性</h3>
                    <p>稳定性: ${info.stable}</p>
                    <p>${info.features}</p>
                </div>
            `;

            document.getElementById('infoGrid').innerHTML = infoHTML;
        }

        // 页面加载完成后初始化
        window.addEventListener('load', init);
    </script>
</body>
</html>$HTML$,
 75,
 0,
 857,
 false,
 0,
 NOW(),
 '{"name": "排序算法可视化", "description": "冒泡排序、快速排序等算法的动态演示", "difficulty": "easy", "render_mode": "html"}');


-- [15/24] 图路径搜索 (computer_science, 75分)
INSERT INTO simulator_templates
(subject, topic, code, quality_score, visual_elements, line_count, has_setup_update, variable_count, created_at, metadata)
VALUES
('computer_science',
 '图路径搜索',
 $HTML$<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>A*寻路算法 - 计算机科学</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
            color: #F1F5F9;
            padding: 20px;
            min-height: 100vh;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        h1 {
            text-align: center;
            color: #06B6D4;
            margin-bottom: 10px;
            font-size: 2em;
            text-shadow: 0 0 20px rgba(6, 182, 212, 0.5);
        }

        .subtitle {
            text-align: center;
            color: #94A3B8;
            margin-bottom: 30px;
            font-size: 1.1em;
        }

        .main-grid {
            display: grid;
            grid-template-columns: 300px 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }

        .controls {
            background: rgba(30, 41, 59, 0.6);
            border: 2px solid #334155;
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            height: fit-content;
        }

        .control-section {
            margin-bottom: 25px;
            padding-bottom: 25px;
            border-bottom: 1px solid #334155;
        }

        .control-section:last-child {
            margin-bottom: 0;
            padding-bottom: 0;
            border-bottom: none;
        }

        .control-section h3 {
            color: #8B5CF6;
            margin-bottom: 15px;
            font-size: 1.1em;
        }

        .control-section p {
            color: #94A3B8;
            font-size: 13px;
            line-height: 1.6;
            margin-bottom: 15px;
        }

        button {
            width: 100%;
            background: linear-gradient(135deg, #06B6D4 0%, #0891B2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 12px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(6, 182, 212, 0.4);
            margin-bottom: 10px;
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(6, 182, 212, 0.6);
        }

        button:active {
            transform: translateY(0);
        }

        button:disabled {
            background: #475569;
            cursor: not-allowed;
            box-shadow: none;
            transform: none;
        }

        .btn-success {
            background: linear-gradient(135deg, #10B981 0%, #059669 100%);
            box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
        }

        .btn-success:hover {
            box-shadow: 0 6px 20px rgba(16, 185, 129, 0.6);
        }

        .btn-danger {
            background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
            box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4);
        }

        .btn-danger:hover {
            box-shadow: 0 6px 20px rgba(239, 68, 68, 0.6);
        }

        .btn-secondary {
            background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
            box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4);
        }

        .btn-secondary:hover {
            box-shadow: 0 6px 20px rgba(139, 92, 246, 0.6);
        }

        .mode-buttons {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 10px;
        }

        .mode-buttons button {
            margin-bottom: 0;
        }

        .visualization {
            background: rgba(30, 41, 59, 0.6);
            border: 2px solid #334155;
            border-radius: 15px;
            padding: 30px;
            backdrop-filter: blur(10px);
        }

        #gridCanvas {
            width: 100%;
            border-radius: 10px;
            cursor: crosshair;
            box-shadow: 0 0 30px rgba(0, 0, 0, 0.5);
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: rgba(30, 41, 59, 0.6);
            border: 2px solid #334155;
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            text-align: center;
        }

        .stat-label {
            color: #94A3B8;
            font-size: 14px;
            margin-bottom: 8px;
        }

        .stat-value {
            color: #06B6D4;
            font-size: 28px;
            font-weight: bold;
        }

        .algorithm-info {
            background: rgba(30, 41, 59, 0.6);
            border: 2px solid #334155;
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(10px);
        }

        .algorithm-info h2 {
            color: #8B5CF6;
            margin-bottom: 15px;
            font-size: 1.5em;
        }

        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }

        .info-item {
            background: rgba(15, 23, 42, 0.5);
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #06B6D4;
        }

        .info-item h3 {
            color: #06B6D4;
            font-size: 16px;
            margin-bottom: 10px;
        }

        .info-item p {
            color: #CBD5E1;
            line-height: 1.8;
            margin-bottom: 10px;
        }

        .formula {
            background: rgba(139, 92, 246, 0.1);
            border: 1px solid #8B5CF6;
            border-radius: 6px;
            padding: 12px;
            font-family: 'Courier New', monospace;
            color: #A78BFA;
            font-size: 14px;
            margin-top: 10px;
        }

        .legend {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 12px;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #334155;
        }

        .legend-item {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 13px;
        }

        .legend-color {
            width: 30px;
            height: 30px;
            border-radius: 6px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        }

        .status-message {
            background: rgba(16, 185, 129, 0.1);
            border: 2px solid #10B981;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            text-align: center;
            color: #10B981;
            font-weight: 600;
            display: none;
        }

        .status-message.show {
            display: block;
            animation: fadeIn 0.3s;
        }

        .status-message.error {
            background: rgba(239, 68, 68, 0.1);
            border-color: #EF4444;
            color: #EF4444;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @media (max-width: 1024px) {
            .main-grid {
                grid-template-columns: 1fr;
            }

            .controls {
                max-width: 600px;
                margin: 0 auto 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🗺️ A*寻路算法可视化</h1>
        <p class="subtitle">探索启发式搜索算法的工作原理</p>

        <div class="status-message" id="statusMessage"></div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-label">已探索节点</div>
                <div class="stat-value" id="exploredNodes">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">路径长度</div>
                <div class="stat-value" id="pathLength">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">搜索耗时</div>
                <div class="stat-value" id="searchTime">0ms</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">开放列表</div>
                <div class="stat-value" id="openList">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">关闭列表</div>
                <div class="stat-value" id="closedList">0</div>
            </div>
        </div>

        <div class="main-grid">
            <div class="controls">
                <div class="control-section">
                    <h3>编辑模式</h3>
                    <p>选择模式后在网格上点击设置</p>
                    <div class="mode-buttons">
                        <button onclick="setMode('start')" class="btn-success" id="startBtn">设置起点</button>
                        <button onclick="setMode('end')" class="btn-danger" id="endBtn">设置终点</button>
                        <button onclick="setMode('wall')" class="btn-secondary" id="wallBtn">绘制墙壁</button>
                        <button onclick="setMode('erase')" id="eraseBtn">擦除</button>
                    </div>
                </div>

                <div class="control-section">
                    <h3>寻路算法</h3>
                    <button onclick="startPathfinding()" class="btn-success">开始寻路</button>
                    <button onclick="clearPath()">清除路径</button>
                    <button onclick="clearAll()">清空网格</button>
                    <button onclick="generateMaze()" class="btn-secondary">生成迷宫</button>
                </div>

                <div class="control-section">
                    <h3>预设场景</h3>
                    <button onclick="loadPreset('simple')">简单路径</button>
                    <button onclick="loadPreset('maze')">复杂迷宫</button>
                    <button onclick="loadPreset('room')">房间布局</button>
                </div>

                <div class="control-section">
                    <h3>当前模式</h3>
                    <p id="currentMode" style="color: #10B981; font-weight: bold;">设置起点</p>
                </div>
            </div>

            <div class="visualization">
                <canvas id="gridCanvas"></canvas>
                <div class="legend">
                    <div class="legend-item">
                        <div class="legend-color" style="background: #10B981;"></div>
                        <span>起点</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #EF4444;"></div>
                        <span>终点</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #1E293B;"></div>
                        <span>墙壁</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #8B5CF6;"></div>
                        <span>开放列表</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #06B6D4;"></div>
                        <span>关闭列表</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #F59E0B;"></div>
                        <span>最短路径</span>
                    </div>
                </div>
            </div>
        </div>

        <div class="algorithm-info">
            <h2>A*算法原理</h2>
            <div class="info-grid">
                <div class="info-item">
                    <h3>算法概述</h3>
                    <p>A*算法是一种启发式搜索算法，用于在图中找到从起点到终点的最短路径。</p>
                    <p>它结合了Dijkstra算法的准确性和贪心最佳优先搜索的效率。</p>
                </div>
                <div class="info-item">
                    <h3>评估函数</h3>
                    <p>A*使用评估函数 f(n) 来选择下一个要探索的节点：</p>
                    <div class="formula">
                        f(n) = g(n) + h(n)
                    </div>
                    <p style="margin-top: 10px;">
                        <strong>g(n)</strong>: 从起点到当前节点的实际代价<br>
                        <strong>h(n)</strong>: 从当前节点到终点的启发式估计
                    </p>
                </div>
                <div class="info-item">
                    <h3>曼哈顿距离</h3>
                    <p>本演示使用曼哈顿距离作为启发式函数：</p>
                    <div class="formula">
                        h(n) = |x₁ - x₂| + |y₁ - y₂|
                    </div>
                    <p style="margin-top: 10px;">这是在网格中只能水平或垂直移动时，两点间的最短距离。</p>
                </div>
                <div class="info-item">
                    <h3>算法步骤</h3>
                    <p><strong>1.</strong> 将起点加入开放列表</p>
                    <p><strong>2.</strong> 选择f值最小的节点探索</p>
                    <p><strong>3.</strong> 将该节点移至关闭列表</p>
                    <p><strong>4.</strong> 检查相邻节点，更新路径</p>
                    <p><strong>5.</strong> 重复直到找到终点</p>
                </div>
                <div class="info-item">
                    <h3>时间复杂度</h3>
                    <p><strong>最佳情况:</strong> O(b^d)</p>
                    <p><strong>平均情况:</strong> O(b^d)</p>
                    <p><strong>最坏情况:</strong> O(b^d)</p>
                    <p style="margin-top: 10px; font-size: 12px;">
                        其中 b 是分支因子，d 是解的深度
                    </p>
                </div>
                <div class="info-item">
                    <h3>算法特性</h3>
                    <p><strong>完备性:</strong> 是（在有限图中）</p>
                    <p><strong>最优性:</strong> 是（启发式可采纳）</p>
                    <p><strong>空间复杂度:</strong> O(b^d)</p>
                    <p style="margin-top: 10px;">适用于游戏AI、路径规划、导航系统</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        const GRID_SIZE = 30;
        const CELL_SIZE = 20;
        let canvas, ctx;
        let grid = [];
        let start = null;
        let end = null;
        let mode = 'start';
        let isDrawing = false;
        let isSearching = false;

        const CELL_TYPES = {
            EMPTY: 0,
            WALL: 1,
            START: 2,
            END: 3,
            OPEN: 4,
            CLOSED: 5,
            PATH: 6
        };

        class Node {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.g = 0;
                this.h = 0;
                this.f = 0;
                this.parent = null;
            }
        }

        // 初始化
        function init() {
            canvas = document.getElementById('gridCanvas');
            ctx = canvas.getContext('2d');

            canvas.width = GRID_SIZE * CELL_SIZE;
            canvas.height = GRID_SIZE * CELL_SIZE;

            initGrid();
            drawGrid();

            canvas.addEventListener('mousedown', handleMouseDown);
            canvas.addEventListener('mousemove', handleMouseMove);
            canvas.addEventListener('mouseup', handleMouseUp);
            canvas.addEventListener('mouseleave', handleMouseUp);

            setMode('start');
        }

        // 初始化网格
        function initGrid() {
            grid = Array(GRID_SIZE).fill(null).map(() =>
                Array(GRID_SIZE).fill(CELL_TYPES.EMPTY)
            );
        }

        // 设置模式
        function setMode(newMode) {
            mode = newMode;

            const buttons = {
                start: 'startBtn',
                end: 'endBtn',
                wall: 'wallBtn',
                erase: 'eraseBtn'
            };

            Object.values(buttons).forEach(id => {
                document.getElementById(id).style.opacity = '0.7';
            });

            if (buttons[mode]) {
                document.getElementById(buttons[mode]).style.opacity = '1';
            }

            const modeText = {
                start: '设置起点',
                end: '设置终点',
                wall: '绘制墙壁',
                erase: '擦除'
            };

            document.getElementById('currentMode').textContent = modeText[mode] || mode;
        }

        // 鼠标事件处理
        function handleMouseDown(e) {
            if (isSearching) return;
            isDrawing = true;
            handleCellClick(e);
        }

        function handleMouseMove(e) {
            if (!isDrawing || isSearching) return;
            if (mode === 'wall' || mode === 'erase') {
                handleCellClick(e);
            }
        }

        function handleMouseUp() {
            isDrawing = false;
        }

        function handleCellClick(e) {
            const rect = canvas.getBoundingClientRect();
            // 计算缩放比例
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
            // 根据缩放比例调整坐标
            const x = Math.floor((e.clientX - rect.left) * scaleX / CELL_SIZE);
            const y = Math.floor((e.clientY - rect.top) * scaleY / CELL_SIZE);

            if (x < 0 || x >= GRID_SIZE || y < 0 || y >= GRID_SIZE) return;

            switch (mode) {
                case 'start':
                    if (start) grid[start.y][start.x] = CELL_TYPES.EMPTY;
                    start = {x, y};
                    grid[y][x] = CELL_TYPES.START;
                    setMode('end');
                    break;
                case 'end':
                    if (end) grid[end.y][end.x] = CELL_TYPES.EMPTY;
                    end = {x, y};
                    grid[y][x] = CELL_TYPES.END;
                    setMode('wall');
                    break;
                case 'wall':
                    if ((start && start.x === x && start.y === y) ||
                        (end && end.x === x && end.y === y)) return;
                    grid[y][x] = CELL_TYPES.WALL;
                    break;
                case 'erase':
                    if ((start && start.x === x && start.y === y) ||
                        (end && end.x === x && end.y === y)) return;
                    grid[y][x] = CELL_TYPES.EMPTY;
                    break;
            }

            drawGrid();
        }

        // 绘制网格
        function drawGrid() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            for (let y = 0; y < GRID_SIZE; y++) {
                for (let x = 0; x < GRID_SIZE; x++) {
                    const cellType = grid[y][x];

                    // 单元格颜色
                    switch (cellType) {
                        case CELL_TYPES.EMPTY:
                            ctx.fillStyle = '#0F172A';
                            break;
                        case CELL_TYPES.WALL:
                            ctx.fillStyle = '#1E293B';
                            break;
                        case CELL_TYPES.START:
                            ctx.fillStyle = '#10B981';
                            break;
                        case CELL_TYPES.END:
                            ctx.fillStyle = '#EF4444';
                            break;
                        case CELL_TYPES.OPEN:
                            ctx.fillStyle = '#8B5CF6';
                            break;
                        case CELL_TYPES.CLOSED:
                            ctx.fillStyle = '#06B6D4';
                            break;
                        case CELL_TYPES.PATH:
                            ctx.fillStyle = '#F59E0B';
                            break;
                    }

                    ctx.fillRect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1);

                    // 起点终点标记
                    if (cellType === CELL_TYPES.START || cellType === CELL_TYPES.END) {
                        ctx.fillStyle = '#FFFFFF';
                        ctx.font = 'bold 12px sans-serif';
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'middle';
                        ctx.fillText(
                            cellType === CELL_TYPES.START ? 'S' : 'E',
                            x * CELL_SIZE + CELL_SIZE / 2,
                            y * CELL_SIZE + CELL_SIZE / 2
                        );
                    }
                }
            }
        }

        // 曼哈顿距离
        function manhattanDistance(a, b) {
            return Math.abs(a.x - b.x) + Math.abs(a.y - b.y);
        }

        // 获取相邻节点
        function getNeighbors(node) {
            const neighbors = [];
            const directions = [[0, 1], [1, 0], [0, -1], [-1, 0]];

            for (const [dx, dy] of directions) {
                const x = node.x + dx;
                const y = node.y + dy;

                if (x >= 0 && x < GRID_SIZE && y >= 0 && y < GRID_SIZE &&
                    grid[y][x] !== CELL_TYPES.WALL) {
                    neighbors.push(new Node(x, y));
                }
            }

            return neighbors;
        }

        // A*寻路算法
        async function startPathfinding() {
            if (!start || !end) {
                showStatus('请先设置起点和终点', 'error');
                return;
            }

            if (isSearching) return;
            isSearching = true;

            // 清除之前的搜索结果
            for (let y = 0; y < GRID_SIZE; y++) {
                for (let x = 0; x < GRID_SIZE; x++) {
                    if (grid[y][x] === CELL_TYPES.OPEN ||
                        grid[y][x] === CELL_TYPES.CLOSED ||
                        grid[y][x] === CELL_TYPES.PATH) {
                        grid[y][x] = CELL_TYPES.EMPTY;
                    }
                }
            }

            grid[start.y][start.x] = CELL_TYPES.START;
            grid[end.y][end.x] = CELL_TYPES.END;

            const startTime = Date.now();
            let exploredCount = 0;

            const openList = [];
            const closedList = new Set();
            const startNode = new Node(start.x, start.y);
            startNode.h = manhattanDistance(start, end);
            startNode.f = startNode.h;
            openList.push(startNode);

            while (openList.length > 0) {
                // 找到f值最小的节点
                openList.sort((a, b) => a.f - b.f);
                const current = openList.shift();

                // 到达终点
                if (current.x === end.x && current.y === end.y) {
                    const path = [];
                    let temp = current;
                    while (temp.parent) {
                        path.unshift({x: temp.x, y: temp.y});
                        temp = temp.parent;
                    }

                    // 绘制路径
                    for (const cell of path) {
                        if (grid[cell.y][cell.x] === CELL_TYPES.EMPTY ||
                            grid[cell.y][cell.x] === CELL_TYPES.CLOSED) {
                            grid[cell.y][cell.x] = CELL_TYPES.PATH;
                            drawGrid();
                            await sleep(30);
                        }
                    }

                    const elapsed = Date.now() - startTime;
                    updateStats(exploredCount, path.length, elapsed, 0, closedList.size);
                    showStatus(`✓ 找到路径！长度: ${path.length}`);
                    isSearching = false;
                    return;
                }

                closedList.add(`${current.x},${current.y}`);
                exploredCount++;

                if (grid[current.y][current.x] !== CELL_TYPES.START &&
                    grid[current.y][current.x] !== CELL_TYPES.END) {
                    grid[current.y][current.x] = CELL_TYPES.CLOSED;
                }

                // 探索邻居节点
                for (const neighbor of getNeighbors(current)) {
                    const key = `${neighbor.x},${neighbor.y}`;

                    if (closedList.has(key)) continue;

                    neighbor.g = current.g + 1;
                    neighbor.h = manhattanDistance(neighbor, end);
                    neighbor.f = neighbor.g + neighbor.h;
                    neighbor.parent = current;

                    const existingIndex = openList.findIndex(n => n.x === neighbor.x && n.y === neighbor.y);

                    if (existingIndex === -1) {
                        openList.push(neighbor);
                        if (grid[neighbor.y][neighbor.x] !== CELL_TYPES.START &&
                            grid[neighbor.y][neighbor.x] !== CELL_TYPES.END) {
                            grid[neighbor.y][neighbor.x] = CELL_TYPES.OPEN;
                        }
                    } else if (neighbor.g < openList[existingIndex].g) {
                        openList[existingIndex] = neighbor;
                    }
                }

                updateStats(exploredCount, 0, Date.now() - startTime, openList.length, closedList.size);
                drawGrid();
                await sleep(20);
            }

            showStatus('无法找到路径', 'error');
            isSearching = false;
        }

        // 更新统计
        function updateStats(explored, pathLen, time, open, closed) {
            document.getElementById('exploredNodes').textContent = explored;
            document.getElementById('pathLength').textContent = pathLen;
            document.getElementById('searchTime').textContent = time + 'ms';
            document.getElementById('openList').textContent = open;
            document.getElementById('closedList').textContent = closed;
        }

        // 清除路径
        function clearPath() {
            for (let y = 0; y < GRID_SIZE; y++) {
                for (let x = 0; x < GRID_SIZE; x++) {
                    if (grid[y][x] === CELL_TYPES.OPEN ||
                        grid[y][x] === CELL_TYPES.CLOSED ||
                        grid[y][x] === CELL_TYPES.PATH) {
                        grid[y][x] = CELL_TYPES.EMPTY;
                    }
                }
            }
            updateStats(0, 0, 0, 0, 0);
            drawGrid();
            showStatus('已清除路径');
        }

        // 清空全部
        function clearAll() {
            initGrid();
            start = null;
            end = null;
            updateStats(0, 0, 0, 0, 0);
            drawGrid();
            setMode('start');
            showStatus('已清空网格');
        }

        // 生成迷宫
        function generateMaze() {
            initGrid();
            start = null;
            end = null;

            for (let y = 0; y < GRID_SIZE; y++) {
                for (let x = 0; x < GRID_SIZE; x++) {
                    if (Math.random() < 0.3) {
                        grid[y][x] = CELL_TYPES.WALL;
                    }
                }
            }

            drawGrid();
            setMode('start');
            showStatus('已生成随机迷宫');
        }

        // 预设场景
        function loadPreset(type) {
            clearAll();

            switch (type) {
                case 'simple':
                    start = {x: 5, y: 15};
                    end = {x: 24, y: 15};
                    grid[15][5] = CELL_TYPES.START;
                    grid[15][24] = CELL_TYPES.END;

                    for (let y = 10; y < 20; y++) {
                        grid[y][15] = CELL_TYPES.WALL;
                    }
                    break;

                case 'maze':
                    start = {x: 2, y: 2};
                    end = {x: 27, y: 27};
                    grid[2][2] = CELL_TYPES.START;
                    grid[27][27] = CELL_TYPES.END;

                    for (let i = 0; i < 10; i++) {
                        const x = Math.floor(Math.random() * (GRID_SIZE - 4)) + 2;
                        const y = Math.floor(Math.random() * (GRID_SIZE - 4)) + 2;
                        const length = Math.floor(Math.random() * 10) + 5;
                        const horizontal = Math.random() < 0.5;

                        for (let j = 0; j < length; j++) {
                            const nx = horizontal ? x + j : x;
                            const ny = horizontal ? y : y + j;
                            if (nx < GRID_SIZE && ny < GRID_SIZE) {
                                grid[ny][nx] = CELL_TYPES.WALL;
                            }
                        }
                    }
                    break;

                case 'room':
                    start = {x: 5, y: 5};
                    end = {x: 24, y: 24};
                    grid[5][5] = CELL_TYPES.START;
                    grid[24][24] = CELL_TYPES.END;

                    // 房间边界
                    for (let i = 3; i < 27; i++) {
                        grid[3][i] = CELL_TYPES.WALL;
                        grid[26][i] = CELL_TYPES.WALL;
                        grid[i][3] = CELL_TYPES.WALL;
                        grid[i][26] = CELL_TYPES.WALL;
                    }

                    // 内部墙壁
                    for (let i = 8; i < 22; i++) {
                        grid[15][i] = CELL_TYPES.WALL;
                    }

                    // 门
                    grid[15][10] = CELL_TYPES.EMPTY;
                    grid[15][19] = CELL_TYPES.EMPTY;
                    grid[8][3] = CELL_TYPES.EMPTY;
                    grid[21][26] = CELL_TYPES.EMPTY;
                    break;
            }

            drawGrid();
            setMode('wall');
            showStatus(`已加载${type}场景`);
        }

        // 显示状态消息
        function showStatus(message, type = 'success') {
            const statusEl = document.getElementById('statusMessage');
            statusEl.textContent = message;
            statusEl.className = 'status-message show';
            if (type === 'error') statusEl.classList.add('error');
            setTimeout(() => statusEl.classList.remove('show'), 3000);
        }

        // 延迟函数
        function sleep(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        }

        // 初始化
        window.addEventListener('load', init);
    </script>
</body>
</html>$HTML$,
 75,
 14,
 924,
 false,
 0,
 NOW(),
 '{"name": "图路径搜索", "description": "图搜索算法（BFS、DFS、Dijkstra）的可视化演示", "difficulty": "hard", "render_mode": "html"}');


-- [16/24] 傅里叶变换 (mathematics, 75分)
INSERT INTO simulator_templates
(subject, topic, code, quality_score, visual_elements, line_count, has_setup_update, variable_count, created_at, metadata)
VALUES
('mathematics',
 '傅里叶变换',
 $HTML$<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>傅里叶变换 - 时域与频域</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #f1f5f9;
            overflow: hidden;
            height: 100vh;
        }

        #canvas {
            display: block;
            width: 100%;
            height: 100%;
            cursor: crosshair;
        }

        .controls {
            position: absolute;
            top: 2vh;
            left: 2vw;
            background: rgba(30, 41, 59, 0.95);
            padding: 2vh 1.5vw;
            border-radius: 1.5vh;
            box-shadow: 0 1vh 3vh rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(100, 116, 139, 0.3);
            max-width: 20vw;
            z-index: 100;
        }

        .controls h2 {
            color: #1e40af;
            margin-bottom: 1.5vh;
            font-size: 1.8vh;
            font-weight: 600;
            text-shadow: 0 0 1vh rgba(30, 64, 175, 0.5);
        }

        .control-group {
            margin-bottom: 2vh;
        }

        .control-group label {
            display: block;
            margin-bottom: 0.8vh;
            font-size: 1.4vh;
            color: #cbd5e1;
            font-weight: 500;
        }

        input[type="range"] {
            width: 100%;
            height: 0.6vh;
            background: rgba(100, 116, 139, 0.3);
            border-radius: 1vh;
            outline: none;
            cursor: pointer;
        }

        input[type="range"]::-webkit-slider-thumb {
            appearance: none;
            width: 2vh;
            height: 2vh;
            background: linear-gradient(135deg, #1e40af 0%, #7c3aed 100%);
            border-radius: 50%;
            cursor: pointer;
            box-shadow: 0 0 1vh rgba(30, 64, 175, 0.8);
        }

        button {
            width: 100%;
            padding: 1.2vh 1vw;
            background: linear-gradient(135deg, #1e40af 0%, #7c3aed 100%);
            color: white;
            border: none;
            border-radius: 0.8vh;
            cursor: pointer;
            font-size: 1.4vh;
            font-weight: 600;
            transition: all 0.3s ease;
            margin-top: 1vh;
            box-shadow: 0 0.4vh 1vh rgba(30, 64, 175, 0.4);
        }

        button:hover {
            transform: translateY(-0.2vh);
            box-shadow: 0 0.6vh 2vh rgba(30, 64, 175, 0.6);
        }

        button:active {
            transform: translateY(0);
        }

        .value-display {
            display: inline-block;
            float: right;
            color: #0ea5e9;
            font-weight: 600;
            font-size: 1.4vh;
        }

        .info-panel {
            position: absolute;
            top: 2vh;
            right: 2vw;
            background: rgba(30, 41, 59, 0.95);
            padding: 2vh 1.5vw;
            border-radius: 1.5vh;
            box-shadow: 0 1vh 3vh rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(100, 116, 139, 0.3);
            max-width: 18vw;
            z-index: 100;
        }

        .info-panel h3 {
            color: #7c3aed;
            margin-bottom: 1vh;
            font-size: 1.6vh;
            text-shadow: 0 0 1vh rgba(124, 58, 237, 0.5);
        }

        .info-item {
            margin: 0.8vh 0;
            font-size: 1.3vh;
            color: #cbd5e1;
        }

        .info-value {
            color: #0ea5e9;
            font-weight: 600;
        }

        .checkbox-group {
            display: flex;
            align-items: center;
            margin: 1vh 0;
        }

        .checkbox-group input[type="checkbox"] {
            width: 1.8vh;
            height: 1.8vh;
            margin-right: 1vw;
            cursor: pointer;
        }

        .checkbox-group label {
            margin-bottom: 0 !important;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <canvas id="canvas"></canvas>

    <div class="controls">
        <h2>🌊 傅里叶变换控制</h2>

        <div class="control-group">
            <label>
                谐波数量
                <span class="value-display" id="harmonicsValue">7</span>
            </label>
            <input type="range" id="harmonics" min="1" max="15" value="7" step="1">
        </div>

        <div class="control-group">
            <label>
                动画速度
                <span class="value-display" id="speedValue">1.0x</span>
            </label>
            <input type="range" id="speed" min="0.1" max="3" value="1" step="0.1">
        </div>

        <div class="control-group">
            <label>
                波形类型
            </label>
            <select id="waveType" style="width: 100%; padding: 1vh; background: rgba(100, 116, 139, 0.3); color: #f1f5f9; border: 1px solid rgba(100, 116, 139, 0.5); border-radius: 0.8vh; font-size: 1.4vh; cursor: pointer;">
                <option value="square">方波</option>
                <option value="sawtooth">锯齿波</option>
                <option value="triangle">三角波</option>
            </select>
        </div>

        <div class="checkbox-group">
            <input type="checkbox" id="showCircles" checked>
            <label for="showCircles">显示旋转圆</label>
        </div>

        <div class="checkbox-group">
            <input type="checkbox" id="showSpectrum" checked>
            <label for="showSpectrum">显示频谱</label>
        </div>

        <button id="resetBtn">🔄 重置动画</button>
    </div>

    <div class="info-panel">
        <h3>📊 傅里叶分析</h3>
        <div class="info-item">
            时间: <span class="info-value" id="timeValue">0.00s</span>
        </div>
        <div class="info-item">
            基频: <span class="info-value" id="freqValue">1.00 Hz</span>
        </div>
        <div class="info-item">
            能量: <span class="info-value" id="energyValue">100%</span>
        </div>
        <div class="info-item" style="margin-top: 1.5vh; padding-top: 1.5vh; border-top: 1px solid rgba(100, 116, 139, 0.3);">
            <strong style="color: #7c3aed;">提示：</strong><br>
            拖动鼠标查看频谱<br>
            点击切换视图模式
        </div>
    </div>

    <script>
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');

        // 响应式画布设置
        function resizeCanvas() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);

        // 配色方案
        const COLORS = {
            primary: '#1E40AF',
            secondary: '#7C3AED',
            accent: '#0EA5E9',
            background: '#1E293B',
            text: '#F1F5F9',
            grid: 'rgba(100, 116, 139, 0.2)',
            glow: 'rgba(30, 64, 175, 0.5)'
        };

        // 状态管理
        const state = {
            time: 0,
            harmonics: 7,
            speed: 1,
            waveType: 'square',
            showCircles: true,
            showSpectrum: true,
            mouseX: 0,
            mouseY: 0,
            isHovering: false,
            waveHistory: [],
            maxHistoryLength: 0
        };

        // 1. 坐标转换辅助函数
        function toCanvasX(x) {
            return canvas.width * x;
        }

        function toCanvasY(y) {
            return canvas.height * y;
        }

        function toRelativeX(canvasX) {
            return canvasX / canvas.width;
        }

        function toRelativeY(canvasY) {
            return canvasY / canvas.height;
        }

        // 2. 缓动函数
        function easeInOutCubic(t) {
            return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
        }

        function easeOutElastic(t) {
            const c4 = (2 * Math.PI) / 3;
            return t === 0 ? 0 : t === 1 ? 1 : Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * c4) + 1;
        }

        function easeInOutQuad(t) {
            return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
        }

        // 3. 波形生成函数
        function getSquareWaveCoefficient(n) {
            return n % 2 === 1 ? 4 / (Math.PI * n) : 0;
        }

        function getSawtoothWaveCoefficient(n) {
            return 2 * Math.pow(-1, n + 1) / (Math.PI * n);
        }

        function getTriangleWaveCoefficient(n) {
            return n % 2 === 1 ? 8 * Math.pow(-1, (n - 1) / 2) / (Math.PI * Math.PI * n * n) : 0;
        }

        function getWaveCoefficient(n, waveType) {
            switch (waveType) {
                case 'square': return getSquareWaveCoefficient(n);
                case 'sawtooth': return getSawtoothWaveCoefficient(n);
                case 'triangle': return getTriangleWaveCoefficient(n);
                default: return 0;
            }
        }

        // 4. 傅里叶级数计算函数
        function calculateFourierPoint(t, harmonics, waveType) {
            let x = 0, y = 0;
            const circles = [];

            for (let i = 1; i <= harmonics; i++) {
                const prevX = x, prevY = y;
                const amplitude = getWaveCoefficient(i, waveType);
                const radius = Math.abs(amplitude) * canvas.height * 0.08;
                const angle = i * t;

                x += radius * Math.cos(angle);
                y += radius * Math.sin(angle);

                circles.push({
                    centerX: prevX,
                    centerY: prevY,
                    radius: radius,
                    angle: angle,
                    endX: x,
                    endY: y,
                    frequency: i,
                    amplitude: amplitude
                });
            }

            return { x, y, circles };
        }

        // 5. 绘制网格函数
        function drawGrid() {
            ctx.strokeStyle = COLORS.grid;
            ctx.lineWidth = 1;

            for (let i = 0; i <= 10; i++) {
                const x = toCanvasX(i / 10);
                const y = toCanvasY(i / 10);

                ctx.beginPath();
                ctx.moveTo(x, 0);
                ctx.lineTo(x, canvas.height);
                ctx.stroke();

                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.lineTo(canvas.width, y);
                ctx.stroke();
            }
        }

        // 6. 绘制旋转圆函数
        function drawRotatingCircles(circles, centerX, centerY) {
            circles.forEach((circle, index) => {
                const alpha = 1 - index * 0.05;

                // 绘制圆
                ctx.strokeStyle = `rgba(30, 64, 175, ${alpha * 0.5})`;
                ctx.lineWidth = 1.5;
                ctx.beginPath();
                ctx.arc(centerX + circle.centerX, centerY + circle.centerY, circle.radius, 0, Math.PI * 2);
                ctx.stroke();

                // 绘制半径线
                ctx.strokeStyle = `rgba(124, 58, 237, ${alpha})`;
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.moveTo(centerX + circle.centerX, centerY + circle.centerY);
                ctx.lineTo(centerX + circle.endX, centerY + circle.endY);
                ctx.stroke();

                // 绘制端点发光效果
                const gradient = ctx.createRadialGradient(
                    centerX + circle.endX, centerY + circle.endY, 0,
                    centerX + circle.endX, centerY + circle.endY, 10
                );
                gradient.addColorStop(0, `rgba(14, 165, 233, ${alpha})`);
                gradient.addColorStop(1, 'rgba(14, 165, 233, 0)');
                ctx.fillStyle = gradient;
                ctx.beginPath();
                ctx.arc(centerX + circle.endX, centerY + circle.endY, 10, 0, Math.PI * 2);
                ctx.fill();
            });
        }

        // 7. 绘制波形历史函数
        function drawWaveHistory(centerY, startX) {
            if (state.waveHistory.length < 2) return;

            ctx.strokeStyle = COLORS.accent;
            ctx.lineWidth = 3;
            ctx.shadowBlur = 10;
            ctx.shadowColor = COLORS.accent;

            ctx.beginPath();
            for (let i = 0; i < state.waveHistory.length; i++) {
                const x = startX + i * 2;
                const y = centerY + state.waveHistory[i];

                if (i === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            }
            ctx.stroke();
            ctx.shadowBlur = 0;
        }

        // 8. 绘制频谱函数
        function drawSpectrum() {
            const spectrumX = toCanvasX(0.75);
            const spectrumY = toCanvasY(0.2);
            const spectrumWidth = toCanvasX(0.2);
            const spectrumHeight = toCanvasY(0.6);

            // 背景
            ctx.fillStyle = 'rgba(30, 41, 59, 0.8)';
            ctx.fillRect(spectrumX, spectrumY, spectrumWidth, spectrumHeight);

            // 标题
            ctx.fillStyle = COLORS.text;
            ctx.font = `${canvas.height * 0.02}px Arial`;
            ctx.textAlign = 'center';
            ctx.fillText('频谱分析', spectrumX + spectrumWidth / 2, spectrumY - canvas.height * 0.02);

            // 绘制频谱条
            const barWidth = spectrumWidth / state.harmonics * 0.7;
            const barSpacing = spectrumWidth / state.harmonics;

            for (let i = 1; i <= state.harmonics; i++) {
                const amplitude = Math.abs(getWaveCoefficient(i, state.waveType));
                const barHeight = amplitude * spectrumHeight * 2;
                const x = spectrumX + (i - 1) * barSpacing + barSpacing / 2 - barWidth / 2;
                const y = spectrumY + spectrumHeight - barHeight;

                // 渐变填充
                const gradient = ctx.createLinearGradient(x, y + barHeight, x, y);
                gradient.addColorStop(0, COLORS.primary);
                gradient.addColorStop(1, COLORS.accent);
                ctx.fillStyle = gradient;
                ctx.fillRect(x, y, barWidth, barHeight);

                // 发光效果
                ctx.shadowBlur = 15;
                ctx.shadowColor = COLORS.accent;
                ctx.fillRect(x, y, barWidth, barHeight);
                ctx.shadowBlur = 0;

                // 频率标签
                ctx.fillStyle = COLORS.text;
                ctx.font = `${canvas.height * 0.015}px Arial`;
                ctx.textAlign = 'center';
                ctx.fillText(`${i}f`, x + barWidth / 2, spectrumY + spectrumHeight + canvas.height * 0.03);
            }
        }

        // 9. 绘制连接线函数
        function drawConnectionLine(x1, y1, x2, y2, alpha = 0.5) {
            ctx.strokeStyle = `rgba(124, 58, 237, ${alpha})`;
            ctx.lineWidth = 1;
            ctx.setLineDash([5, 5]);
            ctx.beginPath();
            ctx.moveTo(x1, y1);
            ctx.lineTo(x2, y2);
            ctx.stroke();
            ctx.setLineDash([]);
        }

        // 10. 绘制坐标轴函数
        function drawAxes(centerX, centerY, width, height) {
            ctx.strokeStyle = COLORS.grid;
            ctx.lineWidth = 2;

            // X轴
            ctx.beginPath();
            ctx.moveTo(centerX - width / 2, centerY);
            ctx.lineTo(centerX + width / 2, centerY);
            ctx.stroke();

            // Y轴
            ctx.beginPath();
            ctx.moveTo(centerX, centerY - height / 2);
            ctx.lineTo(centerX, centerY + height / 2);
            ctx.stroke();

            // 箭头
            const arrowSize = 10;
            ctx.fillStyle = COLORS.grid;
            ctx.beginPath();
            ctx.moveTo(centerX + width / 2, centerY);
            ctx.lineTo(centerX + width / 2 - arrowSize, centerY - arrowSize / 2);
            ctx.lineTo(centerX + width / 2 - arrowSize, centerY + arrowSize / 2);
            ctx.fill();
        }

        // 11. 绘制标签函数
        function drawLabel(text, x, y, size = 0.02) {
            ctx.fillStyle = COLORS.text;
            ctx.font = `${canvas.height * size}px Arial`;
            ctx.textAlign = 'center';
            ctx.fillText(text, x, y);
        }

        // 12. 计算总能量函数
        function calculateTotalEnergy() {
            let energy = 0;
            for (let i = 1; i <= state.harmonics; i++) {
                const amplitude = getWaveCoefficient(i, state.waveType);
                energy += amplitude * amplitude;
            }
            return Math.sqrt(energy);
        }

        // 13. 绘制相位指示器函数
        function drawPhaseIndicator(circles, centerX, centerY) {
            circles.forEach((circle, index) => {
                const phase = (circle.angle % (Math.PI * 2)) / (Math.PI * 2) * 360;
                const x = centerX + circle.centerX;
                const y = centerY + circle.centerY - circle.radius - 20;

                ctx.fillStyle = COLORS.text;
                ctx.font = `${canvas.height * 0.015}px Arial`;
                ctx.textAlign = 'center';
                ctx.fillText(`${Math.round(phase)}°`, x, y);
            });
        }

        // 主渲染函数
        function render() {
            // 清空画布
            ctx.fillStyle = COLORS.background;
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // 绘制网格
            drawGrid();

            // 计算位置
            const centerX = toCanvasX(0.2);
            const centerY = toCanvasY(0.5);
            const waveStartX = toCanvasX(0.4);

            // 计算傅里叶级数
            const result = calculateFourierPoint(state.time, state.harmonics, state.waveType);

            // 绘制旋转圆
            if (state.showCircles) {
                drawRotatingCircles(result.circles, centerX, centerY);
            }

            // 绘制连接线
            drawConnectionLine(centerX + result.x, centerY + result.y, waveStartX, centerY + result.y);

            // 更新波形历史
            state.waveHistory.push(result.y);
            state.maxHistoryLength = toCanvasX(0.5) / 2;
            if (state.waveHistory.length > state.maxHistoryLength) {
                state.waveHistory.shift();
            }

            // 绘制波形
            drawWaveHistory(centerY, waveStartX);

            // 绘制时域坐标轴
            drawAxes(waveStartX + toCanvasX(0.25), centerY, toCanvasX(0.5), toCanvasY(0.6));
            drawLabel('时间 →', waveStartX + toCanvasX(0.48), centerY + toCanvasY(0.02), 0.018);

            // 绘制频谱
            if (state.showSpectrum) {
                drawSpectrum();
            }

            // 更新信息面板
            document.getElementById('timeValue').textContent = (state.time / Math.PI).toFixed(2) + 's';
            document.getElementById('freqValue').textContent = '1.00 Hz';
            const energy = calculateTotalEnergy();
            document.getElementById('energyValue').textContent = Math.round(energy * 100) + '%';

            // 更新时间
            state.time += 0.02 * state.speed;

            requestAnimationFrame(render);
        }

        // 事件监听器
        document.getElementById('harmonics').addEventListener('input', (e) => {
            state.harmonics = parseInt(e.target.value);
            document.getElementById('harmonicsValue').textContent = state.harmonics;
        });

        document.getElementById('speed').addEventListener('input', (e) => {
            state.speed = parseFloat(e.target.value);
            document.getElementById('speedValue').textContent = state.speed.toFixed(1) + 'x';
        });

        document.getElementById('waveType').addEventListener('change', (e) => {
            state.waveType = e.target.value;
            state.waveHistory = [];
        });

        document.getElementById('showCircles').addEventListener('change', (e) => {
            state.showCircles = e.target.checked;
        });

        document.getElementById('showSpectrum').addEventListener('change', (e) => {
            state.showSpectrum = e.target.checked;
        });

        document.getElementById('resetBtn').addEventListener('click', () => {
            state.time = 0;
            state.waveHistory = [];
        });

        canvas.addEventListener('mousemove', (e) => {
            state.mouseX = e.clientX;
            state.mouseY = e.clientY;
            state.isHovering = true;
        });

        canvas.addEventListener('mouseleave', () => {
            state.isHovering = false;
        });

        canvas.addEventListener('click', () => {
            state.showCircles = !state.showCircles;
        });

        // 启动动画
        render();
    </script>
</body>
</html>
$HTML$,
 75,
 86,
 650,
 false,
 0,
 NOW(),
 '{"name": "傅里叶变换", "description": "傅里叶级数的图形展示，展示不同频率波形的叠加", "difficulty": "hard", "render_mode": "html"}');


-- [17/24] 参数曲线 (mathematics, 75分)
INSERT INTO simulator_templates
(subject, topic, code, quality_score, visual_elements, line_count, has_setup_update, variable_count, created_at, metadata)
VALUES
('mathematics',
 '参数曲线',
 $HTML$<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>参数曲线 - 数学之美</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #f1f5f9;
            overflow: hidden;
            height: 100vh;
        }

        #canvas {
            display: block;
            width: 100%;
            height: 100%;
            cursor: crosshair;
        }

        .controls {
            position: absolute;
            top: 2vh;
            left: 2vw;
            background: rgba(30, 41, 59, 0.95);
            padding: 2vh 1.5vw;
            border-radius: 1.5vh;
            box-shadow: 0 1vh 3vh rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(100, 116, 139, 0.3);
            max-width: 22vw;
            z-index: 100;
        }

        .controls h2 {
            color: #1e40af;
            margin-bottom: 1.5vh;
            font-size: 1.8vh;
            font-weight: 600;
            text-shadow: 0 0 1vh rgba(30, 64, 175, 0.5);
        }

        .control-group {
            margin-bottom: 2vh;
        }

        .control-group label {
            display: block;
            margin-bottom: 0.8vh;
            font-size: 1.4vh;
            color: #cbd5e1;
            font-weight: 500;
        }

        input[type="range"] {
            width: 100%;
            height: 0.6vh;
            background: rgba(100, 116, 139, 0.3);
            border-radius: 1vh;
            outline: none;
            cursor: pointer;
        }

        input[type="range"]::-webkit-slider-thumb {
            appearance: none;
            width: 2vh;
            height: 2vh;
            background: linear-gradient(135deg, #1e40af 0%, #7c3aed 100%);
            border-radius: 50%;
            cursor: pointer;
            box-shadow: 0 0 1vh rgba(30, 64, 175, 0.8);
        }

        button {
            width: 100%;
            padding: 1.2vh 1vw;
            background: linear-gradient(135deg, #1e40af 0%, #7c3aed 100%);
            color: white;
            border: none;
            border-radius: 0.8vh;
            cursor: pointer;
            font-size: 1.4vh;
            font-weight: 600;
            transition: all 0.3s ease;
            margin-top: 0.5vh;
            box-shadow: 0 0.4vh 1vh rgba(30, 64, 175, 0.4);
        }

        button:hover {
            transform: translateY(-0.2vh);
            box-shadow: 0 0.6vh 2vh rgba(30, 64, 175, 0.6);
        }

        button.active {
            background: linear-gradient(135deg, #0ea5e9 0%, #7c3aed 100%);
        }

        .value-display {
            display: inline-block;
            float: right;
            color: #0ea5e9;
            font-weight: 600;
            font-size: 1.4vh;
        }

        .info-panel {
            position: absolute;
            top: 2vh;
            right: 2vw;
            background: rgba(30, 41, 59, 0.95);
            padding: 2vh 1.5vw;
            border-radius: 1.5vh;
            box-shadow: 0 1vh 3vh rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(100, 116, 139, 0.3);
            max-width: 20vw;
            z-index: 100;
        }

        .info-panel h3 {
            color: #7c3aed;
            margin-bottom: 1vh;
            font-size: 1.6vh;
            text-shadow: 0 0 1vh rgba(124, 58, 237, 0.5);
        }

        .equation {
            background: rgba(30, 64, 175, 0.1);
            padding: 1vh;
            border-radius: 0.8vh;
            margin: 1vh 0;
            font-family: 'Courier New', monospace;
            font-size: 1.3vh;
            color: #0ea5e9;
            border: 1px solid rgba(30, 64, 175, 0.3);
        }

        .info-item {
            margin: 0.8vh 0;
            font-size: 1.3vh;
            color: #cbd5e1;
        }

        .info-value {
            color: #0ea5e9;
            font-weight: 600;
        }

        .preset-buttons {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 0.5vh;
            margin-top: 1vh;
        }

        .preset-buttons button {
            font-size: 1.2vh;
            padding: 0.8vh;
        }

        .checkbox-group {
            display: flex;
            align-items: center;
            margin: 1vh 0;
        }

        .checkbox-group input[type="checkbox"] {
            width: 1.8vh;
            height: 1.8vh;
            margin-right: 1vw;
            cursor: pointer;
        }

        .checkbox-group label {
            margin-bottom: 0 !important;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <canvas id="canvas"></canvas>

    <div class="controls">
        <h2>📐 参数曲线控制</h2>

        <div class="control-group">
            <label>曲线类型</label>
            <div class="preset-buttons">
                <button id="roseBtn" class="active">玫瑰线</button>
                <button id="cycloidBtn">摆线</button>
                <button id="lissajousBtn">利萨如</button>
                <button id="spiralBtn">螺线</button>
            </div>
        </div>

        <div class="control-group">
            <label>
                参数 n (花瓣数/频率)
                <span class="value-display" id="paramNValue">5</span>
            </label>
            <input type="range" id="paramN" min="1" max="20" value="5" step="1">
        </div>

        <div class="control-group">
            <label>
                参数 d (分母/频率比)
                <span class="value-display" id="paramDValue">1</span>
            </label>
            <input type="range" id="paramD" min="1" max="20" value="1" step="1">
        </div>

        <div class="control-group">
            <label>
                缩放系数
                <span class="value-display" id="scaleValue">1.0</span>
            </label>
            <input type="range" id="scale" min="0.5" max="2" value="1" step="0.1">
        </div>

        <div class="control-group">
            <label>
                动画速度
                <span class="value-display" id="speedValue">1.0x</span>
            </label>
            <input type="range" id="speed" min="0.1" max="3" value="1" step="0.1">
        </div>

        <div class="checkbox-group">
            <input type="checkbox" id="showTrace" checked>
            <label for="showTrace">显示轨迹点</label>
        </div>

        <div class="checkbox-group">
            <input type="checkbox" id="showTangent" checked>
            <label for="showTangent">显示切线</label>
        </div>

        <div class="checkbox-group">
            <input type="checkbox" id="showGrid" checked>
            <label for="showGrid">显示网格</label>
        </div>

        <button id="clearBtn" style="margin-top: 1.5vh;">🗑️ 清除轨迹</button>
    </div>

    <div class="info-panel">
        <h3>📊 参数方程</h3>

        <div class="equation" id="equationDisplay">
            x = r·cos(n·t/d)·cos(t)<br>
            y = r·cos(n·t/d)·sin(t)
        </div>

        <div class="info-item">
            参数 t: <span class="info-value" id="tValue">0.00</span>
        </div>
        <div class="info-item">
            周期: <span class="info-value" id="periodValue">2π</span>
        </div>
        <div class="info-item">
            弧长: <span class="info-value" id="lengthValue">0.00</span>
        </div>
        <div class="info-item">
            曲率: <span class="info-value" id="curvatureValue">0.00</span>
        </div>

        <div style="margin-top: 1.5vh; padding-top: 1.5vh; border-top: 1px solid rgba(100, 116, 139, 0.3);">
            <h3 style="color: #7c3aed; margin-bottom: 1vh; font-size: 1.5vh;">当前坐标</h3>
            <div class="info-item">
                x: <span class="info-value" id="xValue">0.00</span>
            </div>
            <div class="info-item">
                y: <span class="info-value" id="yValue">0.00</span>
            </div>
            <div class="info-item">
                速度: <span class="info-value" id="velocityValue">0.00</span>
            </div>
        </div>

        <div style="margin-top: 1.5vh; font-size: 1.2vh; color: #94a3b8;">
            <strong style="color: #7c3aed;">提示：</strong><br>
            调整n和d观察对称性<br>
            鼠标移动查看切线<br>
            点击切换曲线类型
        </div>
    </div>

    <script>
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');

        // 响应式画布设置
        function resizeCanvas() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);

        // 配色方案
        const COLORS = {
            primary: '#1E40AF',
            secondary: '#7C3AED',
            accent: '#0EA5E9',
            background: '#1E293B',
            text: '#F1F5F9',
            grid: 'rgba(100, 116, 139, 0.2)',
            curve: '#0EA5E9',
            tangent: '#F59E0B',
            trace: '#7C3AED'
        };

        // 状态管理
        const state = {
            curveType: 'rose',
            n: 5,
            d: 1,
            scale: 1,
            speed: 1,
            t: 0,
            showTrace: true,
            showTangent: true,
            showGrid: true,
            tracePoints: [],
            mouseX: 0,
            mouseY: 0,
            curveHistory: [],
            maxHistoryLength: 1000
        };

        // 1. 坐标转换辅助函数
        function toCanvasX(x) {
            return canvas.width / 2 + x;
        }

        function toCanvasY(y) {
            return canvas.height / 2 - y;
        }

        function toRelativeX(canvasX) {
            return (canvasX - canvas.width / 2) / (canvas.width / 2);
        }

        function toRelativeY(canvasY) {
            return (canvas.height / 2 - canvasY) / (canvas.height / 2);
        }

        // 2. 缓动函数
        function easeInOutCubic(t) {
            return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
        }

        function easeOutElastic(t) {
            const c4 = (2 * Math.PI) / 3;
            return t === 0 ? 0 : t === 1 ? 1 : Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * c4) + 1;
        }

        function easeInOutSine(t) {
            return -(Math.cos(Math.PI * t) - 1) / 2;
        }

        // 3. 玫瑰线方程函数
        function roseEquation(t, n, d) {
            const r = Math.cos(n * t / d);
            return {
                x: r * Math.cos(t) * state.scale * Math.min(canvas.width, canvas.height) * 0.3,
                y: r * Math.sin(t) * state.scale * Math.min(canvas.width, canvas.height) * 0.3
            };
        }

        // 4. 摆线方程函数
        function cycloidEquation(t, n, d) {
            const r = Math.min(canvas.width, canvas.height) * 0.05 * state.scale;
            return {
                x: r * n * (t / d - Math.sin(t / d)),
                y: r * n * (1 - Math.cos(t / d))
            };
        }

        // 5. 利萨如曲线方程函数
        function lissajousEquation(t, n, d) {
            const r = Math.min(canvas.width, canvas.height) * 0.3 * state.scale;
            return {
                x: r * Math.sin(n * t / d),
                y: r * Math.sin(t)
            };
        }

        // 6. 螺线方程函数
        function spiralEquation(t, n, d) {
            const r = (t / (Math.PI * 4)) * Math.min(canvas.width, canvas.height) * 0.3 * state.scale;
            const angle = t * n / d;
            return {
                x: r * Math.cos(angle),
                y: r * Math.sin(angle)
            };
        }

        // 7. 通用曲线计算函数
        function calculatePoint(t, curveType, n, d) {
            switch (curveType) {
                case 'rose': return roseEquation(t, n, d);
                case 'cycloid': return cycloidEquation(t, n, d);
                case 'lissajous': return lissajousEquation(t, n, d);
                case 'spiral': return spiralEquation(t, n, d);
                default: return { x: 0, y: 0 };
            }
        }

        // 8. 计算切线函数
        function calculateTangent(t, curveType, n, d) {
            const dt = 0.01;
            const p1 = calculatePoint(t, curveType, n, d);
            const p2 = calculatePoint(t + dt, curveType, n, d);
            return {
                dx: (p2.x - p1.x) / dt,
                dy: (p2.y - p1.y) / dt
            };
        }

        // 9. 计算曲率函数
        function calculateCurvature(t, curveType, n, d) {
            const dt = 0.001;
            const p0 = calculatePoint(t - dt, curveType, n, d);
            const p1 = calculatePoint(t, curveType, n, d);
            const p2 = calculatePoint(t + dt, curveType, n, d);

            const dx = (p2.x - p0.x) / (2 * dt);
            const dy = (p2.y - p0.y) / (2 * dt);
            const ddx = (p2.x - 2 * p1.x + p0.x) / (dt * dt);
            const ddy = (p2.y - 2 * p1.y + p0.y) / (dt * dt);

            const numerator = Math.abs(dx * ddy - dy * ddx);
            const denominator = Math.pow(dx * dx + dy * dy, 1.5);

            return denominator > 0 ? numerator / denominator : 0;
        }

        // 10. 绘制网格函数
        function drawGrid() {
            ctx.strokeStyle = COLORS.grid;
            ctx.lineWidth = 1;

            const gridSize = 50;
            for (let x = 0; x < canvas.width; x += gridSize) {
                ctx.beginPath();
                ctx.moveTo(x, 0);
                ctx.lineTo(x, canvas.height);
                ctx.stroke();
            }
            for (let y = 0; y < canvas.height; y += gridSize) {
                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.lineTo(canvas.width, y);
                ctx.stroke();
            }

            // 绘制坐标轴
            ctx.strokeStyle = 'rgba(100, 116, 139, 0.5)';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(canvas.width / 2, 0);
            ctx.lineTo(canvas.width / 2, canvas.height);
            ctx.moveTo(0, canvas.height / 2);
            ctx.lineTo(canvas.width, canvas.height / 2);
            ctx.stroke();
        }

        // 11. 绘制曲线函数
        function drawCurve() {
            const steps = 1000;
            const maxT = state.curveType === 'spiral' ? state.t : Math.PI * 2 * Math.max(state.n, state.d);

            ctx.strokeStyle = COLORS.curve;
            ctx.lineWidth = 3;
            ctx.shadowBlur = 15;
            ctx.shadowColor = COLORS.curve;

            ctx.beginPath();
            for (let i = 0; i <= steps && i * maxT / steps <= state.t; i++) {
                const t = i * maxT / steps;
                const point = calculatePoint(t, state.curveType, state.n, state.d);
                const x = toCanvasX(point.x);
                const y = toCanvasY(point.y);

                if (i === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            }
            ctx.stroke();
            ctx.shadowBlur = 0;
        }

        // 12. 绘制轨迹点函数
        function drawTracePoints() {
            state.tracePoints.forEach((point, index) => {
                const alpha = (index / state.tracePoints.length) * 0.8;
                const size = 3 + (index / state.tracePoints.length) * 5;

                const gradient = ctx.createRadialGradient(point.x, point.y, 0, point.x, point.y, size);
                gradient.addColorStop(0, `rgba(124, 58, 237, ${alpha})`);
                gradient.addColorStop(1, 'rgba(124, 58, 237, 0)');

                ctx.fillStyle = gradient;
                ctx.beginPath();
                ctx.arc(point.x, point.y, size, 0, Math.PI * 2);
                ctx.fill();
            });
        }

        // 13. 绘制切线函数
        function drawTangentLine(t) {
            const point = calculatePoint(t, state.curveType, state.n, state.d);
            const tangent = calculateTangent(t, state.curveType, state.n, state.d);

            const x = toCanvasX(point.x);
            const y = toCanvasY(point.y);
            const length = 50;
            const norm = Math.sqrt(tangent.dx * tangent.dx + tangent.dy * tangent.dy);

            if (norm > 0) {
                const dx = (tangent.dx / norm) * length;
                const dy = (tangent.dy / norm) * length;

                ctx.strokeStyle = COLORS.tangent;
                ctx.lineWidth = 2;
                ctx.setLineDash([5, 5]);
                ctx.beginPath();
                ctx.moveTo(x - dx, y + dy);
                ctx.lineTo(x + dx, y - dy);
                ctx.stroke();
                ctx.setLineDash([]);
            }
        }

        // 14. 绘制当前点函数
        function drawCurrentPoint(t) {
            const point = calculatePoint(t, state.curveType, state.n, state.d);
            const x = toCanvasX(point.x);
            const y = toCanvasY(point.y);

            // 发光效果
            const gradient = ctx.createRadialGradient(x, y, 0, x, y, 20);
            gradient.addColorStop(0, 'rgba(14, 165, 233, 1)');
            gradient.addColorStop(0.5, 'rgba(14, 165, 233, 0.5)');
            gradient.addColorStop(1, 'rgba(14, 165, 233, 0)');

            ctx.fillStyle = gradient;
            ctx.beginPath();
            ctx.arc(x, y, 20, 0, Math.PI * 2);
            ctx.fill();

            // 中心点
            ctx.fillStyle = '#ffffff';
            ctx.beginPath();
            ctx.arc(x, y, 5, 0, Math.PI * 2);
            ctx.fill();
        }

        // 15. 绘制参数标注函数
        function drawParameterLabel(t) {
            const point = calculatePoint(t, state.curveType, state.n, state.d);
            const x = toCanvasX(point.x);
            const y = toCanvasY(point.y);

            ctx.fillStyle = COLORS.text;
            ctx.font = `${canvas.height * 0.02}px Arial`;
            ctx.textAlign = 'center';
            ctx.fillText(`t = ${t.toFixed(2)}`, x, y - 30);
        }

        // 16. 更新方程显示函数
        function updateEquationDisplay() {
            const equations = {
                rose: `x = r·cos(${state.n}t/${state.d})·cos(t)<br>y = r·cos(${state.n}t/${state.d})·sin(t)`,
                cycloid: `x = ${state.n}r(t/${state.d} - sin(t/${state.d}))<br>y = ${state.n}r(1 - cos(t/${state.d}))`,
                lissajous: `x = r·sin(${state.n}t/${state.d})<br>y = r·sin(t)`,
                spiral: `x = (t/4π)r·cos(${state.n}t/${state.d})<br>y = (t/4π)r·sin(${state.n}t/${state.d})`
            };
            document.getElementById('equationDisplay').innerHTML = equations[state.curveType];
        }

        // 17. 计算周期函数
        function calculatePeriod() {
            const periods = {
                rose: `${2 * Math.PI * Math.max(state.n, state.d)}`,
                cycloid: `${2 * Math.PI * state.d}`,
                lissajous: `${2 * Math.PI * Math.max(state.n, state.d)}`,
                spiral: '∞'
            };
            return periods[state.curveType];
        }

        // 18. 计算弧长函数
        function calculateArcLength(t) {
            const steps = 100;
            let length = 0;

            for (let i = 0; i < steps && i * t / steps <= t; i++) {
                const t1 = i * t / steps;
                const t2 = (i + 1) * t / steps;
                const p1 = calculatePoint(t1, state.curveType, state.n, state.d);
                const p2 = calculatePoint(t2, state.curveType, state.n, state.d);
                const dx = p2.x - p1.x;
                const dy = p2.y - p1.y;
                length += Math.sqrt(dx * dx + dy * dy);
            }

            return length;
        }

        // 19. 绘制装饰圆环函数
        function drawDecorativeCircles() {
            const point = calculatePoint(state.t, state.curveType, state.n, state.d);
            const x = toCanvasX(point.x);
            const y = toCanvasY(point.y);

            for (let i = 1; i <= 3; i++) {
                ctx.strokeStyle = `rgba(124, 58, 237, ${0.3 / i})`;
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.arc(x, y, 10 * i, 0, Math.PI * 2);
                ctx.stroke();
            }
        }

        // 主渲染函数
        function render() {
            // 清空画布
            ctx.fillStyle = COLORS.background;
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // 绘制网格
            if (state.showGrid) {
                drawGrid();
            }

            // 绘制曲线
            drawCurve();

            // 绘制轨迹点
            if (state.showTrace) {
                drawTracePoints();
            }

            // 绘制切线
            if (state.showTangent) {
                drawTangentLine(state.t);
            }

            // 绘制装饰圆环
            drawDecorativeCircles();

            // 绘制当前点
            drawCurrentPoint(state.t);

            // 绘制参数标注
            drawParameterLabel(state.t);

            // 更新轨迹点
            const point = calculatePoint(state.t, state.curveType, state.n, state.d);
            state.tracePoints.push({
                x: toCanvasX(point.x),
                y: toCanvasY(point.y)
            });
            if (state.tracePoints.length > 50) {
                state.tracePoints.shift();
            }

            // 更新信息面板
            document.getElementById('tValue').textContent = state.t.toFixed(2);
            document.getElementById('periodValue').textContent = calculatePeriod();
            document.getElementById('lengthValue').textContent = calculateArcLength(state.t).toFixed(2);
            document.getElementById('curvatureValue').textContent = calculateCurvature(state.t, state.curveType, state.n, state.d).toFixed(4);
            document.getElementById('xValue').textContent = point.x.toFixed(2);
            document.getElementById('yValue').textContent = point.y.toFixed(2);

            const tangent = calculateTangent(state.t, state.curveType, state.n, state.d);
            const velocity = Math.sqrt(tangent.dx * tangent.dx + tangent.dy * tangent.dy);
            document.getElementById('velocityValue').textContent = velocity.toFixed(2);

            // 更新时间参数
            state.t += 0.02 * state.speed;
            if (state.curveType !== 'spiral' && state.t > Math.PI * 2 * Math.max(state.n, state.d)) {
                state.t = 0;
            }

            requestAnimationFrame(render);
        }

        // 事件监听器
        document.getElementById('paramN').addEventListener('input', (e) => {
            state.n = parseInt(e.target.value);
            document.getElementById('paramNValue').textContent = state.n;
            updateEquationDisplay();
            state.t = 0;
            state.tracePoints = [];
        });

        document.getElementById('paramD').addEventListener('input', (e) => {
            state.d = parseInt(e.target.value);
            document.getElementById('paramDValue').textContent = state.d;
            updateEquationDisplay();
            state.t = 0;
            state.tracePoints = [];
        });

        document.getElementById('scale').addEventListener('input', (e) => {
            state.scale = parseFloat(e.target.value);
            document.getElementById('scaleValue').textContent = state.scale.toFixed(1);
        });

        document.getElementById('speed').addEventListener('input', (e) => {
            state.speed = parseFloat(e.target.value);
            document.getElementById('speedValue').textContent = state.speed.toFixed(1) + 'x';
        });

        document.getElementById('showTrace').addEventListener('change', (e) => {
            state.showTrace = e.target.checked;
        });

        document.getElementById('showTangent').addEventListener('change', (e) => {
            state.showTangent = e.target.checked;
        });

        document.getElementById('showGrid').addEventListener('change', (e) => {
            state.showGrid = e.target.checked;
        });

        document.getElementById('clearBtn').addEventListener('click', () => {
            state.tracePoints = [];
        });

        // 曲线类型切换
        function setCurveType(type) {
            state.curveType = type;
            state.t = 0;
            state.tracePoints = [];
            updateEquationDisplay();

            document.querySelectorAll('.preset-buttons button').forEach(btn => {
                btn.classList.remove('active');
            });
            document.getElementById(type + 'Btn').classList.add('active');
        }

        document.getElementById('roseBtn').addEventListener('click', () => setCurveType('rose'));
        document.getElementById('cycloidBtn').addEventListener('click', () => setCurveType('cycloid'));
        document.getElementById('lissajousBtn').addEventListener('click', () => setCurveType('lissajous'));
        document.getElementById('spiralBtn').addEventListener('click', () => setCurveType('spiral'));

        canvas.addEventListener('mousemove', (e) => {
            state.mouseX = e.clientX;
            state.mouseY = e.clientY;
        });

        // 初始化
        updateEquationDisplay();
        render();
    </script>
</body>
</html>
$HTML$,
 75,
 60,
 772,
 false,
 0,
 NOW(),
 '{"name": "参数曲线", "description": "参数方程生成的各种美丽曲线（心形线、玫瑰线等）", "difficulty": "medium", "render_mode": "html"}');


-- [18/24] 矩阵运算 (mathematics, 75分)
INSERT INTO simulator_templates
(subject, topic, code, quality_score, visual_elements, line_count, has_setup_update, variable_count, created_at, metadata)
VALUES
('mathematics',
 '矩阵运算',
 $HTML$<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>矩阵运算 - 线性变换可视化</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #f1f5f9;
            overflow: hidden;
            height: 100vh;
        }

        #canvas {
            display: block;
            width: 100%;
            height: 100%;
            cursor: grab;
        }

        #canvas:active {
            cursor: grabbing;
        }

        .controls {
            position: absolute;
            top: 2vh;
            left: 2vw;
            background: rgba(30, 41, 59, 0.95);
            padding: 2vh 1.5vw;
            border-radius: 1.5vh;
            box-shadow: 0 1vh 3vh rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(100, 116, 139, 0.3);
            max-width: 22vw;
            z-index: 100;
        }

        .controls h2 {
            color: #1e40af;
            margin-bottom: 1.5vh;
            font-size: 1.8vh;
            font-weight: 600;
            text-shadow: 0 0 1vh rgba(30, 64, 175, 0.5);
        }

        .control-group {
            margin-bottom: 2vh;
        }

        .control-group label {
            display: block;
            margin-bottom: 0.8vh;
            font-size: 1.4vh;
            color: #cbd5e1;
            font-weight: 500;
        }

        input[type="range"] {
            width: 100%;
            height: 0.6vh;
            background: rgba(100, 116, 139, 0.3);
            border-radius: 1vh;
            outline: none;
            cursor: pointer;
        }

        input[type="range"]::-webkit-slider-thumb {
            appearance: none;
            width: 2vh;
            height: 2vh;
            background: linear-gradient(135deg, #1e40af 0%, #7c3aed 100%);
            border-radius: 50%;
            cursor: pointer;
            box-shadow: 0 0 1vh rgba(30, 64, 175, 0.8);
        }

        button {
            width: 100%;
            padding: 1.2vh 1vw;
            background: linear-gradient(135deg, #1e40af 0%, #7c3aed 100%);
            color: white;
            border: none;
            border-radius: 0.8vh;
            cursor: pointer;
            font-size: 1.4vh;
            font-weight: 600;
            transition: all 0.3s ease;
            margin-top: 0.5vh;
            box-shadow: 0 0.4vh 1vh rgba(30, 64, 175, 0.4);
        }

        button:hover {
            transform: translateY(-0.2vh);
            box-shadow: 0 0.6vh 2vh rgba(30, 64, 175, 0.6);
        }

        button:active {
            transform: translateY(0);
        }

        button.secondary {
            background: linear-gradient(135deg, #64748b 0%, #475569 100%);
        }

        .value-display {
            display: inline-block;
            float: right;
            color: #0ea5e9;
            font-weight: 600;
            font-size: 1.4vh;
        }

        .matrix-display {
            position: absolute;
            top: 2vh;
            right: 2vw;
            background: rgba(30, 41, 59, 0.95);
            padding: 2vh 1.5vw;
            border-radius: 1.5vh;
            box-shadow: 0 1vh 3vh rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(100, 116, 139, 0.3);
            max-width: 20vw;
            z-index: 100;
        }

        .matrix-display h3 {
            color: #7c3aed;
            margin-bottom: 1vh;
            font-size: 1.6vh;
            text-shadow: 0 0 1vh rgba(124, 58, 237, 0.5);
        }

        .matrix {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1vh;
            margin: 1.5vh 0;
            padding: 1.5vh;
            background: rgba(30, 64, 175, 0.1);
            border-radius: 0.8vh;
            border: 1px solid rgba(30, 64, 175, 0.3);
        }

        .matrix-cell {
            text-align: center;
            font-size: 1.6vh;
            font-weight: 600;
            color: #0ea5e9;
            font-family: 'Courier New', monospace;
        }

        .info-item {
            margin: 0.8vh 0;
            font-size: 1.3vh;
            color: #cbd5e1;
        }

        .info-value {
            color: #0ea5e9;
            font-weight: 600;
        }

        .preset-buttons {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 0.5vh;
            margin-top: 1vh;
        }

        .preset-buttons button {
            font-size: 1.2vh;
            padding: 0.8vh;
        }
    </style>
</head>
<body>
    <canvas id="canvas"></canvas>

    <div class="controls">
        <h2>🔢 矩阵变换控制</h2>

        <div class="control-group">
            <label>
                矩阵 a (缩放X/旋转)
                <span class="value-display" id="aValue">1.00</span>
            </label>
            <input type="range" id="matrixA" min="-2" max="2" value="1" step="0.1">
        </div>

        <div class="control-group">
            <label>
                矩阵 b (剪切/旋转)
                <span class="value-display" id="bValue">0.00</span>
            </label>
            <input type="range" id="matrixB" min="-2" max="2" value="0" step="0.1">
        </div>

        <div class="control-group">
            <label>
                矩阵 c (剪切/旋转)
                <span class="value-display" id="cValue">0.00</span>
            </label>
            <input type="range" id="matrixC" min="-2" max="2" value="0" step="0.1">
        </div>

        <div class="control-group">
            <label>
                矩阵 d (缩放Y/旋转)
                <span class="value-display" id="dValue">1.00</span>
            </label>
            <input type="range" id="matrixD" min="-2" max="2" value="1" step="0.1">
        </div>

        <div class="control-group">
            <label>
                动画速度
                <span class="value-display" id="speedValue">0.5x</span>
            </label>
            <input type="range" id="animSpeed" min="0" max="2" value="0.5" step="0.1">
        </div>

        <button id="animateBtn">▶ 动画演示</button>
        <button id="resetBtn" class="secondary">🔄 重置</button>

        <div style="margin-top: 1.5vh; padding-top: 1.5vh; border-top: 1px solid rgba(100, 116, 139, 0.3);">
            <label style="font-size: 1.3vh; color: #cbd5e1; margin-bottom: 0.8vh; display: block;">预设变换</label>
            <div class="preset-buttons">
                <button id="rotateBtn">旋转</button>
                <button id="scaleBtn">缩放</button>
                <button id="shearBtn">剪切</button>
                <button id="reflectBtn">镜像</button>
            </div>
        </div>
    </div>

    <div class="matrix-display">
        <h3>📐 变换矩阵</h3>

        <div class="matrix">
            <div class="matrix-cell" id="cell-a">1.00</div>
            <div class="matrix-cell" id="cell-b">0.00</div>
            <div class="matrix-cell" id="cell-c">0.00</div>
            <div class="matrix-cell" id="cell-d">1.00</div>
        </div>

        <div class="info-item">
            行列式: <span class="info-value" id="detValue">1.00</span>
        </div>
        <div class="info-item">
            迹(trace): <span class="info-value" id="traceValue">2.00</span>
        </div>
        <div class="info-item">
            面积缩放: <span class="info-value" id="scaleValue">1.00x</span>
        </div>
        <div class="info-item">
            变换类型: <span class="info-value" id="typeValue">恒等变换</span>
        </div>

        <div style="margin-top: 1.5vh; padding-top: 1.5vh; border-top: 1px solid rgba(100, 116, 139, 0.3);">
            <h3 style="color: #7c3aed; margin-bottom: 1vh; font-size: 1.5vh;">特征值</h3>
            <div class="info-item">
                λ₁: <span class="info-value" id="eigen1Value">1.00</span>
            </div>
            <div class="info-item">
                λ₂: <span class="info-value" id="eigen2Value">1.00</span>
            </div>
        </div>

        <div style="margin-top: 1.5vh; font-size: 1.2vh; color: #94a3b8;">
            <strong style="color: #7c3aed;">提示：</strong><br>
            拖动鼠标旋转视角<br>
            拖动滑块调整矩阵<br>
            点击预设快速变换
        </div>
    </div>

    <script>
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');

        // 响应式画布设置
        function resizeCanvas() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);

        // 配色方案
        const COLORS = {
            primary: '#1E40AF',
            secondary: '#7C3AED',
            accent: '#0EA5E9',
            background: '#1E293B',
            text: '#F1F5F9',
            grid: 'rgba(100, 116, 139, 0.2)',
            gridBold: 'rgba(100, 116, 139, 0.4)',
            vector1: '#0EA5E9',
            vector2: '#7C3AED',
            transformed1: '#F59E0B',
            transformed2: '#EF4444'
        };

        // 状态管理
        const state = {
            matrix: { a: 1, b: 0, c: 0, d: 1 },
            targetMatrix: { a: 1, b: 0, c: 0, d: 1 },
            animating: false,
            animProgress: 0,
            animSpeed: 0.5,
            gridSize: 50,
            mouseX: 0,
            mouseY: 0,
            dragging: false,
            time: 0,
            rotationX: 0,
            rotationY: 0,
            rotationZ: 0,
            lastMouseX: 0,
            lastMouseY: 0
        };

        // 1. 坐标转换辅助函数
        function toCanvasX(x) {
            return canvas.width / 2 + x;
        }

        function toCanvasY(y) {
            return canvas.height / 2 - y;
        }

        function toMathX(canvasX) {
            return canvasX - canvas.width / 2;
        }

        function toMathY(canvasY) {
            return canvas.height / 2 - canvasY;
        }

        // 3D旋转变换函数
        function apply3DRotation(x, y, z = 0) {
            // 先应用绕X轴旋转
            let cosX = Math.cos(state.rotationX);
            let sinX = Math.sin(state.rotationX);
            let y1 = y * cosX - z * sinX;
            let z1 = y * sinX + z * cosX;

            // 绕Y轴旋转
            let cosY = Math.cos(state.rotationY);
            let sinY = Math.sin(state.rotationY);
            let x2 = x * cosY + z1 * sinY;
            let z2 = -x * sinY + z1 * cosY;

            // 绕Z轴旋转
            let cosZ = Math.cos(state.rotationZ);
            let sinZ = Math.sin(state.rotationZ);
            let x3 = x2 * cosZ - y1 * sinZ;
            let y3 = x2 * sinZ + y1 * cosZ;

            return { x: x3, y: y3, z: z2 };
        }

        // 2. 缓动函数
        function easeInOutCubic(t) {
            return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
        }

        function easeOutElastic(t) {
            const c4 = (2 * Math.PI) / 3;
            return t === 0 ? 0 : t === 1 ? 1 : Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * c4) + 1;
        }

        function easeInOutBack(t) {
            const c1 = 1.70158;
            const c2 = c1 * 1.525;
            return t < 0.5
                ? (Math.pow(2 * t, 2) * ((c2 + 1) * 2 * t - c2)) / 2
                : (Math.pow(2 * t - 2, 2) * ((c2 + 1) * (t * 2 - 2) + c2) + 2) / 2;
        }

        // 3. 矩阵运算函数
        function matrixMultiply(m, x, y) {
            return {
                x: m.a * x + m.b * y,
                y: m.c * x + m.d * y
            };
        }

        function matrixDeterminant(m) {
            return m.a * m.d - m.b * m.c;
        }

        function matrixTrace(m) {
            return m.a + m.d;
        }

        function calculateEigenvalues(m) {
            const trace = matrixTrace(m);
            const det = matrixDeterminant(m);
            const discriminant = trace * trace - 4 * det;

            if (discriminant >= 0) {
                const sqrtDisc = Math.sqrt(discriminant);
                return {
                    lambda1: (trace + sqrtDisc) / 2,
                    lambda2: (trace - sqrtDisc) / 2
                };
            } else {
                const real = trace / 2;
                const imag = Math.sqrt(-discriminant) / 2;
                return {
                    lambda1: { real, imag },
                    lambda2: { real, imag: -imag }
                };
            }
        }

        // 4. 矩阵插值函数
        function interpolateMatrix(m1, m2, t) {
            const eased = easeInOutCubic(t);
            return {
                a: m1.a + (m2.a - m1.a) * eased,
                b: m1.b + (m2.b - m1.b) * eased,
                c: m1.c + (m2.c - m1.c) * eased,
                d: m1.d + (m2.d - m1.d) * eased
            };
        }

        // 5. 绘制网格函数
        function drawGrid(matrix) {
            const gridRange = 10;

            // 绘制垂直线
            for (let i = -gridRange; i <= gridRange; i++) {
                const start = matrixMultiply(matrix, i * state.gridSize, -gridRange * state.gridSize);
                const end = matrixMultiply(matrix, i * state.gridSize, gridRange * state.gridSize);

                // 应用3D旋转
                const start3D = apply3DRotation(start.x, start.y, 0);
                const end3D = apply3DRotation(end.x, end.y, 0);

                ctx.strokeStyle = i === 0 ? COLORS.gridBold : COLORS.grid;
                ctx.lineWidth = i === 0 ? 2 : 1;
                ctx.beginPath();
                ctx.moveTo(toCanvasX(start3D.x), toCanvasY(start3D.y));
                ctx.lineTo(toCanvasX(end3D.x), toCanvasY(end3D.y));
                ctx.stroke();
            }

            // 绘制水平线
            for (let i = -gridRange; i <= gridRange; i++) {
                const start = matrixMultiply(matrix, -gridRange * state.gridSize, i * state.gridSize);
                const end = matrixMultiply(matrix, gridRange * state.gridSize, i * state.gridSize);

                // 应用3D旋转
                const start3D = apply3DRotation(start.x, start.y, 0);
                const end3D = apply3DRotation(end.x, end.y, 0);

                ctx.strokeStyle = i === 0 ? COLORS.gridBold : COLORS.grid;
                ctx.lineWidth = i === 0 ? 2 : 1;
                ctx.beginPath();
                ctx.moveTo(toCanvasX(start3D.x), toCanvasY(start3D.y));
                ctx.lineTo(toCanvasX(end3D.x), toCanvasY(end3D.y));
                ctx.stroke();
            }
        }

        // 6. 绘制向量函数
        function drawVector(x, y, color, label, glowIntensity = 1) {
            // 应用3D旋转
            const rotated = apply3DRotation(x, y, 0);
            const endX = toCanvasX(rotated.x);
            const endY = toCanvasY(rotated.y);
            const startX = toCanvasX(0);
            const startY = toCanvasY(0);

            // 发光效果
            ctx.shadowBlur = 15 * glowIntensity;
            ctx.shadowColor = color;

            // 绘制向量线
            ctx.strokeStyle = color;
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.moveTo(startX, startY);
            ctx.lineTo(endX, endY);
            ctx.stroke();

            // 绘制箭头
            const angle = Math.atan2(rotated.y, rotated.x);
            const arrowLength = 15;
            const arrowAngle = Math.PI / 6;

            ctx.fillStyle = color;
            ctx.beginPath();
            ctx.moveTo(endX, endY);
            ctx.lineTo(
                endX - arrowLength * Math.cos(angle - arrowAngle),
                endY + arrowLength * Math.sin(angle - arrowAngle)
            );
            ctx.lineTo(
                endX - arrowLength * Math.cos(angle + arrowAngle),
                endY + arrowLength * Math.sin(angle + arrowAngle)
            );
            ctx.closePath();
            ctx.fill();

            ctx.shadowBlur = 0;

            // 绘制标签
            ctx.fillStyle = COLORS.text;
            ctx.font = `${canvas.height * 0.02}px Arial`;
            ctx.textAlign = 'center';
            ctx.fillText(label, endX + 20, endY - 20);
        }

        // 7. 绘制基向量函数
        function drawBasisVectors(matrix) {
            // i 向量 (1, 0) -> (a, c)
            const i = matrixMultiply(matrix, state.gridSize * 2, 0);
            drawVector(i.x, i.y, COLORS.vector1, 'i', 1);

            // j 向量 (0, 1) -> (b, d)
            const j = matrixMultiply(matrix, 0, state.gridSize * 2);
            drawVector(j.x, j.y, COLORS.vector2, 'j', 1);
        }

        // 8. 绘制测试图形函数
        function drawTestShape(matrix) {
            const shapes = [
                // 正方形
                {points: [[1, 1], [1, -1], [-1, -1], [-1, 1]], color: COLORS.accent},
                // 三角形
                {points: [[0, 1.5], [-1, -0.5], [1, -0.5]], color: COLORS.secondary}
            ];

            shapes.forEach(shape => {
                ctx.strokeStyle = shape.color;
                ctx.lineWidth = 2;
                ctx.setLineDash([]);

                // 原始形状（虚线）
                ctx.globalAlpha = 0.3;
                ctx.setLineDash([5, 5]);
                ctx.beginPath();
                shape.points.forEach((point, i) => {
                    const rotated = apply3DRotation(point[0] * state.gridSize, point[1] * state.gridSize, 0);
                    const x = toCanvasX(rotated.x);
                    const y = toCanvasY(rotated.y);
                    if (i === 0) ctx.moveTo(x, y);
                    else ctx.lineTo(x, y);
                });
                ctx.closePath();
                ctx.stroke();

                // 变换后形状（实线）
                ctx.globalAlpha = 1;
                ctx.setLineDash([]);
                ctx.shadowBlur = 10;
                ctx.shadowColor = shape.color;
                ctx.beginPath();
                shape.points.forEach((point, i) => {
                    const transformed = matrixMultiply(matrix, point[0] * state.gridSize, point[1] * state.gridSize);
                    const rotated = apply3DRotation(transformed.x, transformed.y, 0);
                    const x = toCanvasX(rotated.x);
                    const y = toCanvasY(rotated.y);
                    if (i === 0) ctx.moveTo(x, y);
                    else ctx.lineTo(x, y);
                });
                ctx.closePath();
                ctx.stroke();
                ctx.shadowBlur = 0;
            });
        }

        // 9. 绘制单位圆函数
        function drawUnitCircle(matrix) {
            const points = 64;
            ctx.strokeStyle = COLORS.accent;
            ctx.lineWidth = 2;

            // 原始单位圆（虚线）
            ctx.globalAlpha = 0.3;
            ctx.setLineDash([5, 5]);
            ctx.beginPath();
            for (let i = 0; i <= points; i++) {
                const angle = (i / points) * Math.PI * 2;
                const x = Math.cos(angle) * state.gridSize;
                const y = Math.sin(angle) * state.gridSize;
                const rotated = apply3DRotation(x, y, 0);
                const canvasX = toCanvasX(rotated.x);
                const canvasY = toCanvasY(rotated.y);
                if (i === 0) ctx.moveTo(canvasX, canvasY);
                else ctx.lineTo(canvasX, canvasY);
            }
            ctx.stroke();

            // 变换后椭圆（实线）
            ctx.globalAlpha = 1;
            ctx.setLineDash([]);
            ctx.shadowBlur = 10;
            ctx.shadowColor = COLORS.accent;
            ctx.beginPath();
            for (let i = 0; i <= points; i++) {
                const angle = (i / points) * Math.PI * 2;
                const x = Math.cos(angle) * state.gridSize;
                const y = Math.sin(angle) * state.gridSize;
                const transformed = matrixMultiply(matrix, x, y);
                const rotated = apply3DRotation(transformed.x, transformed.y, 0);
                const canvasX = toCanvasX(rotated.x);
                const canvasY = toCanvasY(rotated.y);
                if (i === 0) ctx.moveTo(canvasX, canvasY);
                else ctx.lineTo(canvasX, canvasY);
            }
            ctx.stroke();
            ctx.shadowBlur = 0;
        }

        // 10. 绘制特征向量函数
        function drawEigenvectors(matrix) {
            const eigenvalues = calculateEigenvalues(matrix);
            if (typeof eigenvalues.lambda1 === 'object') return; // 复数特征值

            // 计算特征向量
            const lambda1 = eigenvalues.lambda1;
            const lambda2 = eigenvalues.lambda2;

            // 特征向量1
            let v1x, v1y;
            if (Math.abs(matrix.b) > 0.001) {
                v1x = 1;
                v1y = (lambda1 - matrix.a) / matrix.b;
            } else {
                v1x = lambda1 - matrix.d;
                v1y = 1;
            }
            const norm1 = Math.sqrt(v1x * v1x + v1y * v1y);
            v1x = (v1x / norm1) * state.gridSize * 1.5;
            v1y = (v1y / norm1) * state.gridSize * 1.5;

            const rotated1 = apply3DRotation(v1x, v1y, 0);
            drawVector(v1x, v1y, COLORS.transformed1, `v₁ (λ=${lambda1.toFixed(2)})`, 0.7);

            // 特征向量2
            if (Math.abs(lambda1 - lambda2) > 0.001) {
                let v2x, v2y;
                if (Math.abs(matrix.b) > 0.001) {
                    v2x = 1;
                    v2y = (lambda2 - matrix.a) / matrix.b;
                } else {
                    v2x = lambda2 - matrix.d;
                    v2y = 1;
                }
                const norm2 = Math.sqrt(v2x * v2x + v2y * v2y);
                v2x = (v2x / norm2) * state.gridSize * 1.5;
                v2y = (v2y / norm2) * state.gridSize * 1.5;

                drawVector(v2x, v2y, COLORS.transformed2, `v₂ (λ=${lambda2.toFixed(2)})`, 0.7);
            }
        }

        // 11. 绘制坐标轴标签函数
        function drawAxisLabels() {
            ctx.fillStyle = COLORS.text;
            ctx.font = `${canvas.height * 0.02}px Arial`;
            ctx.textAlign = 'center';

            // X轴
            ctx.fillText('x', toCanvasX(canvas.width * 0.4), toCanvasY(-20));
            // Y轴
            ctx.fillText('y', toCanvasX(20), toCanvasY(canvas.height * 0.4));
        }

        // 12. 判断变换类型函数
        function getTransformationType(m) {
            const det = matrixDeterminant(m);
            const isIdentity = Math.abs(m.a - 1) < 0.01 && Math.abs(m.d - 1) < 0.01 &&
                             Math.abs(m.b) < 0.01 && Math.abs(m.c) < 0.01;

            if (isIdentity) return '恒等变换';
            if (Math.abs(det) < 0.01) return '投影/退化';
            if (Math.abs(m.b) < 0.01 && Math.abs(m.c) < 0.01) return '缩放';
            if (Math.abs(det - 1) < 0.01 && Math.abs(m.a * m.a + m.c * m.c - 1) < 0.01) return '旋转';
            if (Math.abs(m.a - m.d) < 0.01 && Math.abs(m.b + m.c) < 0.01) return '旋转+缩放';
            if (Math.abs(m.a - 1) < 0.01 || Math.abs(m.d - 1) < 0.01) return '剪切';
            if (det < 0) return '镜像+变换';
            return '一般线性变换';
        }

        // 13. 更新UI显示函数
        function updateMatrixDisplay() {
            const m = state.matrix;

            document.getElementById('cell-a').textContent = m.a.toFixed(2);
            document.getElementById('cell-b').textContent = m.b.toFixed(2);
            document.getElementById('cell-c').textContent = m.c.toFixed(2);
            document.getElementById('cell-d').textContent = m.d.toFixed(2);

            const det = matrixDeterminant(m);
            const trace = matrixTrace(m);

            document.getElementById('detValue').textContent = det.toFixed(2);
            document.getElementById('traceValue').textContent = trace.toFixed(2);
            document.getElementById('scaleValue').textContent = Math.abs(det).toFixed(2) + 'x';
            document.getElementById('typeValue').textContent = getTransformationType(m);

            const eigenvalues = calculateEigenvalues(m);
            if (typeof eigenvalues.lambda1 === 'object') {
                document.getElementById('eigen1Value').textContent =
                    `${eigenvalues.lambda1.real.toFixed(2)}±${eigenvalues.lambda1.imag.toFixed(2)}i`;
                document.getElementById('eigen2Value').textContent = '(复数)';
            } else {
                document.getElementById('eigen1Value').textContent = eigenvalues.lambda1.toFixed(2);
                document.getElementById('eigen2Value').textContent = eigenvalues.lambda2.toFixed(2);
            }
        }

        // 主渲染函数
        function render() {
            // 动画插值
            if (state.animating) {
                state.animProgress += 0.01 * state.animSpeed;
                if (state.animProgress >= 1) {
                    state.animProgress = 1;
                    state.animating = false;
                }
                state.matrix = interpolateMatrix(
                    { a: 1, b: 0, c: 0, d: 1 },
                    state.targetMatrix,
                    state.animProgress
                );
                updateMatrixDisplay();
            }

            // 清空画布
            ctx.fillStyle = COLORS.background;
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // 绘制网格
            drawGrid(state.matrix);

            // 绘制坐标轴标签
            drawAxisLabels();

            // 绘制测试图形
            drawTestShape(state.matrix);

            // 绘制单位圆
            drawUnitCircle(state.matrix);

            // 绘制基向量
            drawBasisVectors(state.matrix);

            // 绘制特征向量
            drawEigenvectors(state.matrix);

            state.time += 0.01;
            requestAnimationFrame(render);
        }

        // 事件监听器
        document.getElementById('matrixA').addEventListener('input', (e) => {
            state.matrix.a = parseFloat(e.target.value);
            state.targetMatrix.a = state.matrix.a;
            document.getElementById('aValue').textContent = state.matrix.a.toFixed(2);
            updateMatrixDisplay();
        });

        document.getElementById('matrixB').addEventListener('input', (e) => {
            state.matrix.b = parseFloat(e.target.value);
            state.targetMatrix.b = state.matrix.b;
            document.getElementById('bValue').textContent = state.matrix.b.toFixed(2);
            updateMatrixDisplay();
        });

        document.getElementById('matrixC').addEventListener('input', (e) => {
            state.matrix.c = parseFloat(e.target.value);
            state.targetMatrix.c = state.matrix.c;
            document.getElementById('cValue').textContent = state.matrix.c.toFixed(2);
            updateMatrixDisplay();
        });

        document.getElementById('matrixD').addEventListener('input', (e) => {
            state.matrix.d = parseFloat(e.target.value);
            state.targetMatrix.d = state.matrix.d;
            document.getElementById('dValue').textContent = state.matrix.d.toFixed(2);
            updateMatrixDisplay();
        });

        document.getElementById('animSpeed').addEventListener('input', (e) => {
            state.animSpeed = parseFloat(e.target.value);
            document.getElementById('speedValue').textContent = state.animSpeed.toFixed(1) + 'x';
        });

        document.getElementById('animateBtn').addEventListener('click', () => {
            state.animating = true;
            state.animProgress = 0;
        });

        document.getElementById('resetBtn').addEventListener('click', () => {
            state.matrix = { a: 1, b: 0, c: 0, d: 1 };
            state.targetMatrix = { a: 1, b: 0, c: 0, d: 1 };
            document.getElementById('matrixA').value = 1;
            document.getElementById('matrixB').value = 0;
            document.getElementById('matrixC').value = 0;
            document.getElementById('matrixD').value = 1;
            document.getElementById('aValue').textContent = '1.00';
            document.getElementById('bValue').textContent = '0.00';
            document.getElementById('cValue').textContent = '0.00';
            document.getElementById('dValue').textContent = '1.00';
            updateMatrixDisplay();
        });

        // 预设变换
        document.getElementById('rotateBtn').addEventListener('click', () => {
            const angle = Math.PI / 4;
            state.targetMatrix = {
                a: Math.cos(angle),
                b: -Math.sin(angle),
                c: Math.sin(angle),
                d: Math.cos(angle)
            };
            state.animating = true;
            state.animProgress = 0;
        });

        document.getElementById('scaleBtn').addEventListener('click', () => {
            state.targetMatrix = { a: 1.5, b: 0, c: 0, d: 0.5 };
            state.animating = true;
            state.animProgress = 0;
        });

        document.getElementById('shearBtn').addEventListener('click', () => {
            state.targetMatrix = { a: 1, b: 0.5, c: 0.5, d: 1 };
            state.animating = true;
            state.animProgress = 0;
        });

        document.getElementById('reflectBtn').addEventListener('click', () => {
            state.targetMatrix = { a: -1, b: 0, c: 0, d: 1 };
            state.animating = true;
            state.animProgress = 0;
        });

        // 鼠标拖动控制3D旋转
        canvas.addEventListener('mousedown', (e) => {
            state.dragging = true;
            state.lastMouseX = e.clientX;
            state.lastMouseY = e.clientY;
        });

        canvas.addEventListener('mousemove', (e) => {
            if (state.dragging) {
                const deltaX = e.clientX - state.lastMouseX;
                const deltaY = e.clientY - state.lastMouseY;

                state.rotationY += deltaX * 0.01;
                state.rotationX += deltaY * 0.01;

                state.lastMouseX = e.clientX;
                state.lastMouseY = e.clientY;
            }
        });

        canvas.addEventListener('mouseup', () => {
            state.dragging = false;
        });

        canvas.addEventListener('mouseleave', () => {
            state.dragging = false;
        });

        // 启动动画
        updateMatrixDisplay();
        render();
    </script>
</body>
</html>
$HTML$,
 75,
 76,
 888,
 false,
 0,
 NOW(),
 '{"name": "矩阵运算", "description": "矩阵乘法、变换的几何意义可视化", "difficulty": "medium", "render_mode": "html"}');


-- [19/24] 历史事件因果关系 (history, 75分)
INSERT INTO simulator_templates
(subject, topic, code, quality_score, visual_elements, line_count, has_setup_update, variable_count, created_at, metadata)
VALUES
('history',
 '历史事件因果关系',
 $HTML$<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>历史事件因果关系 - 历史模拟器</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
            color: #F1F5F9;
            min-height: 100vh;
            padding: 20px;
            overflow-x: hidden;
        }

        .container {
            max-width: 1600px;
            margin: 0 auto;
        }

        header {
            text-align: center;
            margin-bottom: 30px;
            padding: 30px;
            background: rgba(146, 64, 14, 0.1);
            border-radius: 15px;
            border: 2px solid #92400E;
        }

        h1 {
            color: #CA8A04;
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 0 0 20px rgba(202, 138, 4, 0.5);
        }

        .subtitle {
            color: #94A3B8;
            font-size: 1.1em;
        }

        .controls {
            background: rgba(30, 41, 59, 0.8);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            border: 1px solid #334155;
        }

        .control-group {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        label {
            color: #CA8A04;
            font-weight: bold;
        }

        select {
            background: #334155;
            color: #F1F5F9;
            border: 1px solid #92400E;
            padding: 8px 12px;
            border-radius: 5px;
            cursor: pointer;
        }

        button {
            background: linear-gradient(135deg, #92400E, #78350F);
            color: #F1F5F9;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(202, 138, 4, 0.3);
        }

        .graph-container {
            background: rgba(30, 41, 59, 0.6);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            border: 2px solid #334155;
            min-height: 700px;
            position: relative;
        }

        #network {
            width: 100%;
            height: 650px;
            position: relative;
        }

        .node {
            position: absolute;
            background: linear-gradient(135deg, #92400E, #78350F);
            border: 3px solid #CA8A04;
            border-radius: 15px;
            padding: 15px 20px;
            cursor: pointer;
            transition: all 0.3s;
            min-width: 180px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
            z-index: 10;
        }

        .node:hover {
            transform: scale(1.1);
            box-shadow: 0 10px 30px rgba(202, 138, 4, 0.5);
            z-index: 20;
        }

        .node.selected {
            border-color: #FCD34D;
            box-shadow: 0 0 30px rgba(252, 211, 77, 0.8);
            transform: scale(1.15);
            z-index: 25;
        }

        .node.cause {
            background: linear-gradient(135deg, #DC2626, #991B1B);
            border-color: #F87171;
        }

        .node.effect {
            background: linear-gradient(135deg, #2563EB, #1E40AF);
            border-color: #60A5FA;
        }

        .node.major {
            border-width: 4px;
            font-size: 1.1em;
            min-width: 220px;
            padding: 20px 25px;
        }

        .node-title {
            font-weight: bold;
            margin-bottom: 5px;
            font-size: 1.05em;
        }

        .node-year {
            font-size: 0.85em;
            color: #FCD34D;
            margin-top: 5px;
        }

        .node-detail {
            font-size: 0.8em;
            color: #CBD5E1;
            margin-top: 8px;
            display: none;
        }

        .node.expanded .node-detail {
            display: block;
        }

        .connection {
            position: absolute;
            height: 0;
            border-top: 3px solid #CA8A04;
            transform-origin: left center;
            pointer-events: none;
            z-index: 1;
            opacity: 0.6;
        }

        .connection::after {
            content: '';
            position: absolute;
            right: -10px;
            top: -6px;
            width: 0;
            height: 0;
            border-left: 12px solid #CA8A04;
            border-top: 6px solid transparent;
            border-bottom: 6px solid transparent;
        }

        .connection.highlighted {
            border-color: #FCD34D;
            border-width: 4px;
            opacity: 1;
            animation: pulse 2s infinite;
        }

        .connection.highlighted::after {
            border-left-color: #FCD34D;
            right: -12px;
            top: -8px;
            border-left-width: 16px;
            border-top-width: 8px;
            border-bottom-width: 8px;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .info-panel {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }

        .info-card {
            background: rgba(30, 41, 59, 0.8);
            padding: 25px;
            border-radius: 10px;
            border: 2px solid #334155;
        }

        .info-card h2 {
            color: #CA8A04;
            margin-bottom: 15px;
            border-bottom: 2px solid #92400E;
            padding-bottom: 10px;
        }

        .event-detail {
            background: rgba(51, 65, 85, 0.5);
            padding: 20px;
            border-radius: 8px;
            margin-top: 15px;
            border-left: 4px solid #CA8A04;
        }

        .detail-section {
            margin-bottom: 15px;
        }

        .detail-label {
            color: #FCD34D;
            font-weight: bold;
            margin-bottom: 8px;
            font-size: 1.05em;
        }

        .detail-content {
            color: #CBD5E1;
            line-height: 1.6;
            margin-left: 10px;
        }

        .cause-effect-list {
            margin-top: 10px;
        }

        .cause-effect-item {
            background: rgba(30, 41, 59, 0.6);
            padding: 10px 15px;
            border-radius: 6px;
            margin-bottom: 8px;
            border-left: 3px solid #CA8A04;
            cursor: pointer;
            transition: all 0.3s;
        }

        .cause-effect-item:hover {
            background: rgba(51, 65, 85, 0.8);
            transform: translateX(5px);
            border-left-color: #FCD34D;
        }

        .analysis-section {
            background: rgba(51, 65, 85, 0.5);
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
        }

        .analysis-title {
            color: #CA8A04;
            font-weight: bold;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .analysis-content {
            color: #CBD5E1;
            line-height: 1.8;
        }

        .legend {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 20px;
            flex-wrap: wrap;
            background: rgba(30, 41, 59, 0.6);
            padding: 15px;
            border-radius: 10px;
        }

        .legend-item {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .legend-box {
            width: 30px;
            height: 30px;
            border-radius: 5px;
            border: 2px solid #CA8A04;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }

        .stat-box {
            background: rgba(51, 65, 85, 0.5);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }

        .stat-number {
            font-size: 2em;
            color: #CA8A04;
            font-weight: bold;
            margin: 5px 0;
        }

        .stat-label {
            color: #94A3B8;
            font-size: 0.85em;
        }

        @media (max-width: 1024px) {
            .info-panel {
                grid-template-columns: 1fr;
            }
        }

        @media (max-width: 768px) {
            h1 {
                font-size: 1.8em;
            }

            #network {
                height: 500px;
            }

            .node {
                min-width: 140px;
                padding: 12px 15px;
                font-size: 0.9em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔗 历史事件因果关系网络</h1>
            <p class="subtitle">探索历史事件的因果链 | 多因多果 · 复杂关联</p>
        </header>

        <div class="controls">
            <div class="control-group">
                <label>选择历史事件：</label>
                <select id="eventSelect" onchange="selectEvent(this.value)">
                    <option value="">请选择事件</option>
                    <option value="opium-war">鸦片战争</option>
                    <option value="xinhai">辛亥革命</option>
                    <option value="anshi">安史之乱</option>
                    <option value="reform">戊戌变法</option>
                </select>
            </div>

            <div class="control-group">
                <button onclick="showCauses()">查看原因</button>
                <button onclick="showEffects()">查看影响</button>
                <button onclick="expandAll()">展开全部</button>
                <button onclick="resetView()">重置视图</button>
            </div>
        </div>

        <div class="graph-container">
            <div id="network"></div>
            <div class="legend">
                <div class="legend-item">
                    <div class="legend-box" style="background: linear-gradient(135deg, #DC2626, #991B1B);"></div>
                    <span>原因/前因</span>
                </div>
                <div class="legend-item">
                    <div class="legend-box" style="background: linear-gradient(135deg, #92400E, #78350F);"></div>
                    <span>核心事件</span>
                </div>
                <div class="legend-item">
                    <div class="legend-box" style="background: linear-gradient(135deg, #2563EB, #1E40AF);"></div>
                    <span>结果/影响</span>
                </div>
            </div>
        </div>

        <div class="info-panel">
            <div class="info-card">
                <h2>📋 事件详情</h2>
                <div id="eventInfo">
                    <p style="color: #94A3B8;">点击或选择事件查看详细信息</p>
                </div>
            </div>

            <div class="info-card">
                <h2>🔍 因果分析</h2>
                <div id="analysisInfo">
                    <div class="stats-grid">
                        <div class="stat-box">
                            <div class="stat-label">直接原因</div>
                            <div class="stat-number" id="directCauses">0</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-label">深层原因</div>
                            <div class="stat-number" id="rootCauses">0</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-label">直接影响</div>
                            <div class="stat-number" id="directEffects">0</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-label">长远影响</div>
                            <div class="stat-number" id="longEffects">0</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const events = {
            'opium-war': {
                id: 'opium-war',
                title: '鸦片战争',
                year: '1840-1842',
                description: '英国为打开中国市场，以禁烟为借口发动的侵略战争，是中国近代史的开端。',
                causes: [
                    { id: 'trade-deficit', title: '贸易逆差', year: '1800s', desc: '英国对华贸易长期逆差，白银大量外流' },
                    { id: 'opium-trade', title: '鸦片走私', year: '1820s', desc: '英国商人向中国大量走私鸦片，牟取暴利', type: 'major' },
                    { id: 'lin-destroy', title: '虎门销烟', year: '1839', desc: '林则徐在虎门销毁鸦片，英国借此发动战争', type: 'major' },
                    { id: 'closed-door', title: '闭关锁国', year: '1757-', desc: '清朝实行闭关锁国政策，限制对外贸易' }
                ],
                effects: [
                    { id: 'treaty-nanjing', title: '南京条约', year: '1842', desc: '中国被迫签订第一个不平等条约，割地赔款', type: 'major' },
                    { id: 'semi-colonial', title: '半殖民地化', year: '1840-', desc: '中国开始沦为半殖民地半封建社会', type: 'major' },
                    { id: 'open-ports', title: '开放通商口岸', year: '1842-', desc: '被迫开放五个通商口岸，西方势力深入' },
                    { id: 'loss-sovereignty', title: '主权丧失', year: '1842-', desc: '关税自主权、司法主权等开始丧失' },
                    { id: 'modern-start', title: '近代史开端', year: '1840', desc: '标志着中国近代史的开始' }
                ]
            },
            'xinhai': {
                id: 'xinhai',
                title: '辛亥革命',
                year: '1911',
                description: '推翻清朝统治，结束君主专制制度的资产阶级民主革命。',
                causes: [
                    { id: 'qing-corrupt', title: '清政府腐败', year: '1800s', desc: '清政府统治腐败，民不聊生', type: 'major' },
                    { id: 'foreign-invasion', title: '列强侵略', year: '1840-', desc: '西方列强不断侵略，民族危机加深' },
                    { id: 'new-class', title: '资产阶级兴起', year: '1900s', desc: '民族资产阶级成长，要求民主权利' },
                    { id: 'reform-fail', title: '变法失败', year: '1898', desc: '戊戌变法失败，改良道路行不通', type: 'major' }
                ],
                effects: [
                    { id: 'end-monarchy', title: '结束帝制', year: '1912', desc: '推翻清朝统治，结束两千年君主专制', type: 'major' },
                    { id: 'republic', title: '建立共和', year: '1912', desc: '建立中华民国，实行共和制', type: 'major' },
                    { id: 'ideology-change', title: '思想解放', year: '1911-', desc: '民主共和观念深入人心' },
                    { id: 'warlord', title: '军阀混战', year: '1916-', desc: '革命果实被窃取，陷入军阀混战' }
                ]
            },
            'anshi': {
                id: 'anshi',
                title: '安史之乱',
                year: '755-763',
                description: '唐朝安禄山、史思明发动的叛乱，是唐朝由盛转衰的转折点。',
                causes: [
                    { id: 'frontier-power', title: '藩镇势力', year: '740s', desc: '边境节度使权力过大，尾大不掉' },
                    { id: 'emperor-neglect', title: '玄宗晚年', year: '740s', desc: '唐玄宗晚年荒于政事，朝政腐败', type: 'major' },
                    { id: 'yang-guifei', title: '杨贵妃专宠', year: '740s', desc: '杨国忠等外戚专权，政治混乱' },
                    { id: 'an-power', title: '安禄山势力', year: '750s', desc: '安禄山身兼三镇节度使，实力强大', type: 'major' }
                ],
                effects: [
                    { id: 'tang-decline', title: '唐朝衰落', year: '755-', desc: '唐朝由盛转衰，中央权威削弱', type: 'major' },
                    { id: 'population-loss', title: '人口锐减', year: '755-763', desc: '战争导致人口大量减少，经济破坏' },
                    { id: 'frontier-lost', title: '边疆丧失', year: '760s', desc: '西域等边疆地区大量丧失' },
                    { id: 'separatism', title: '藩镇割据', year: '763-', desc: '形成藩镇割据局面，中央难以控制', type: 'major' }
                ]
            },
            'reform': {
                id: 'reform',
                title: '戊戌变法',
                year: '1898',
                description: '康有为、梁启超等维新派推动的自上而下的改良运动。',
                causes: [
                    { id: 'jiawu-defeat', title: '甲午战败', year: '1895', desc: '甲午战争失败，民族危机空前严重', type: 'major' },
                    { id: 'western-learning', title: '西学传播', year: '1860s-', desc: '西方思想传入，启蒙思想发展' },
                    { id: 'meiji-success', title: '日本维新', year: '1868-', desc: '日本明治维新成功，给中国启示' },
                    { id: 'bourgeois-grow', title: '资产阶级成长', year: '1890s', desc: '民族资产阶级力量增强，要求变法' }
                ],
                effects: [
                    { id: 'reform-fail', title: '变法失败', year: '1898', desc: '百日维新最终失败，变法派被镇压', type: 'major' },
                    { id: 'six-martyrs', title: '六君子遇害', year: '1898', desc: '谭嗣同等戊戌六君子被杀' },
                    { id: 'ideology-spread', title: '思想传播', year: '1898-', desc: '虽然失败，但维新思想得到传播' },
                    { id: 'reform-impossible', title: '改良行不通', year: '1898', desc: '证明改良道路在中国行不通', type: 'major' }
                ]
            }
        };

        let selectedEvent = null;
        let expandedNodes = new Set();

        function selectEvent(eventId) {
            if (!eventId) return;

            selectedEvent = events[eventId];
            renderNetwork();
            showEventDetails();
        }

        function renderNetwork() {
            const network = document.getElementById('network');
            network.innerHTML = '';

            if (!selectedEvent) return;

            const centerX = network.offsetWidth / 2;
            const centerY = network.offsetHeight / 2;

            // Render central event
            createNode(selectedEvent, centerX - 110, centerY - 40, 'center');

            // Render causes (left side)
            const causeRadius = 280;
            selectedEvent.causes.forEach((cause, index) => {
                const angle = (Math.PI / 2) + (index - (selectedEvent.causes.length - 1) / 2) * (Math.PI / (selectedEvent.causes.length + 1));
                const x = centerX - causeRadius * Math.cos(angle) - 90;
                const y = centerY - causeRadius * Math.sin(angle) - 30;

                createNode(cause, x, y, 'cause');
                createConnection(x + 90, y + 30, centerX - 90, centerY + 30, cause.id, selectedEvent.id);
            });

            // Render effects (right side)
            const effectRadius = 280;
            selectedEvent.effects.forEach((effect, index) => {
                const angle = (Math.PI / 2) + (index - (selectedEvent.effects.length - 1) / 2) * (Math.PI / (selectedEvent.effects.length + 1));
                const x = centerX + effectRadius * Math.cos(angle) - 90;
                const y = centerY - effectRadius * Math.sin(angle) - 30;

                createNode(effect, x, y, 'effect');
                createConnection(centerX + 110, centerY + 30, x, y + 30, selectedEvent.id, effect.id);
            });

            updateStats();
        }

        function createNode(data, x, y, type) {
            const node = document.createElement('div');
            node.className = `node ${type} ${data.type || ''}`;
            node.id = `node-${data.id || 'center'}`;
            node.style.left = x + 'px';
            node.style.top = y + 'px';

            node.innerHTML = `
                <div class="node-title">${data.title}</div>
                <div class="node-year">${data.year}</div>
                <div class="node-detail">${data.description || data.desc}</div>
            `;

            node.onclick = (e) => {
                e.stopPropagation();
                toggleNodeExpansion(data.id || 'center');
                if (type === 'center') {
                    showEventDetails();
                }
            };

            document.getElementById('network').appendChild(node);
        }

        function createConnection(x1, y1, x2, y2, fromId, toId) {
            const length = Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
            const angle = Math.atan2(y2 - y1, x2 - x1) * (180 / Math.PI);

            const connection = document.createElement('div');
            connection.className = 'connection';
            connection.id = `conn-${fromId}-${toId}`;
            connection.style.left = x1 + 'px';
            connection.style.top = y1 + 'px';
            connection.style.width = length + 'px';
            connection.style.transform = `rotate(${angle}deg)`;

            document.getElementById('network').appendChild(connection);
        }

        function toggleNodeExpansion(nodeId) {
            const node = document.getElementById(`node-${nodeId}`);
            if (!node) return;

            if (expandedNodes.has(nodeId)) {
                expandedNodes.delete(nodeId);
                node.classList.remove('expanded');
            } else {
                expandedNodes.add(nodeId);
                node.classList.add('expanded');
            }
        }

        function showEventDetails() {
            if (!selectedEvent) return;

            const infoDiv = document.getElementById('eventInfo');
            infoDiv.innerHTML = `
                <div class="event-detail">
                    <div class="detail-section">
                        <div class="detail-label">📅 时间</div>
                        <div class="detail-content">${selectedEvent.year}</div>
                    </div>
                    <div class="detail-section">
                        <div class="detail-label">📖 简介</div>
                        <div class="detail-content">${selectedEvent.description}</div>
                    </div>
                    <div class="detail-section">
                        <div class="detail-label">🔴 主要原因</div>
                        <div class="cause-effect-list">
                            ${selectedEvent.causes.filter(c => c.type === 'major').map(c => `
                                <div class="cause-effect-item" onclick="highlightNode('${c.id}')">
                                    ${c.title} (${c.year})
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    <div class="detail-section">
                        <div class="detail-label">🔵 主要影响</div>
                        <div class="cause-effect-list">
                            ${selectedEvent.effects.filter(e => e.type === 'major').map(e => `
                                <div class="cause-effect-item" onclick="highlightNode('${e.id}')">
                                    ${e.title} (${e.year})
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            `;
        }

        function highlightNode(nodeId) {
            // Remove previous highlights
            document.querySelectorAll('.node').forEach(n => n.classList.remove('selected'));
            document.querySelectorAll('.connection').forEach(c => c.classList.remove('highlighted'));

            // Highlight selected node
            const node = document.getElementById(`node-${nodeId}`);
            if (node) {
                node.classList.add('selected');

                // Highlight connections
                document.querySelectorAll(`.connection[id*="${nodeId}"]`).forEach(c => {
                    c.classList.add('highlighted');
                });
            }
        }

        function showCauses() {
            if (!selectedEvent) return;

            document.querySelectorAll('.node.cause').forEach(node => {
                node.classList.add('selected');
            });

            selectedEvent.causes.forEach(cause => {
                const conn = document.getElementById(`conn-${cause.id}-${selectedEvent.id}`);
                if (conn) conn.classList.add('highlighted');
            });

            setTimeout(() => {
                document.querySelectorAll('.node, .connection').forEach(el => {
                    el.classList.remove('selected', 'highlighted');
                });
            }, 3000);
        }

        function showEffects() {
            if (!selectedEvent) return;

            document.querySelectorAll('.node.effect').forEach(node => {
                node.classList.add('selected');
            });

            selectedEvent.effects.forEach(effect => {
                const conn = document.getElementById(`conn-${selectedEvent.id}-${effect.id}`);
                if (conn) conn.classList.add('highlighted');
            });

            setTimeout(() => {
                document.querySelectorAll('.node, .connection').forEach(el => {
                    el.classList.remove('selected', 'highlighted');
                });
            }, 3000);
        }

        function expandAll() {
            document.querySelectorAll('.node').forEach(node => {
                node.classList.add('expanded');
            });
        }

        function resetView() {
            expandedNodes.clear();
            document.querySelectorAll('.node').forEach(node => {
                node.classList.remove('expanded', 'selected');
            });
            document.querySelectorAll('.connection').forEach(conn => {
                conn.classList.remove('highlighted');
            });
        }

        function updateStats() {
            if (!selectedEvent) return;

            const directCauses = selectedEvent.causes.filter(c => c.type === 'major').length;
            const rootCauses = selectedEvent.causes.length - directCauses;
            const directEffects = selectedEvent.effects.filter(e => e.type === 'major').length;
            const longEffects = selectedEvent.effects.length - directEffects;

            document.getElementById('directCauses').textContent = directCauses;
            document.getElementById('rootCauses').textContent = rootCauses;
            document.getElementById('directEffects').textContent = directEffects;
            document.getElementById('longEffects').textContent = longEffects;
        }

        // Initialize with first event
        window.addEventListener('load', () => {
            document.getElementById('eventSelect').value = 'opium-war';
            selectEvent('opium-war');
        });

        window.addEventListener('resize', () => {
            if (selectedEvent) renderNetwork();
        });
    </script>
</body>
</html>$HTML$,
 75,
 0,
 770,
 false,
 0,
 NOW(),
 '{"name": "历史事件因果关系", "description": "重大历史事件的因果链条和相互影响关系图", "difficulty": "medium", "render_mode": "html"}');


-- [20/24] 贸易路线 (history, 75分)
INSERT INTO simulator_templates
(subject, topic, code, quality_score, visual_elements, line_count, has_setup_update, variable_count, created_at, metadata)
VALUES
('history',
 '贸易路线',
 $HTML$<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>古代贸易路线 - 历史模拟器</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
            color: #F1F5F9;
            min-height: 100vh;
            padding: 20px;
            overflow-x: hidden;
        }

        .container {
            max-width: 1600px;
            margin: 0 auto;
        }

        header {
            text-align: center;
            margin-bottom: 30px;
            padding: 30px;
            background: rgba(146, 64, 14, 0.1);
            border-radius: 15px;
            border: 2px solid #92400E;
        }

        h1 {
            color: #CA8A04;
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 0 0 20px rgba(202, 138, 4, 0.5);
        }

        .subtitle {
            color: #94A3B8;
            font-size: 1.1em;
        }

        .controls {
            background: rgba(30, 41, 59, 0.8);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            border: 1px solid #334155;
        }

        .control-group {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        label {
            color: #CA8A04;
            font-weight: bold;
        }

        button {
            background: linear-gradient(135deg, #92400E, #78350F);
            color: #F1F5F9;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(202, 138, 4, 0.3);
        }

        button.active {
            background: linear-gradient(135deg, #CA8A04, #92400E);
            box-shadow: 0 0 20px rgba(202, 138, 4, 0.4);
        }

        .map-container {
            background: rgba(30, 41, 59, 0.6);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            border: 2px solid #334155;
            position: relative;
        }

        #map {
            width: 100%;
            height: 600px;
            background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #334155 100%);
            border-radius: 10px;
            position: relative;
            overflow: hidden;
            border: 2px solid #475569;
        }

        .city {
            position: absolute;
            width: 16px;
            height: 16px;
            background: #CA8A04;
            border: 3px solid #FCD34D;
            border-radius: 50%;
            cursor: pointer;
            transition: all 0.3s;
            z-index: 10;
            box-shadow: 0 0 10px rgba(202, 138, 4, 0.5);
        }

        .city:hover {
            transform: scale(1.8);
            box-shadow: 0 0 25px rgba(252, 211, 77, 0.8);
            z-index: 50;
        }

        .city.major {
            width: 20px;
            height: 20px;
            background: #F59E0B;
        }

        .city-label {
            position: absolute;
            bottom: 25px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(30, 41, 59, 0.95);
            padding: 5px 12px;
            border-radius: 6px;
            font-size: 0.85em;
            white-space: nowrap;
            border: 1px solid #CA8A04;
            display: none;
            font-weight: bold;
        }

        .city:hover .city-label {
            display: block;
        }

        .route {
            position: absolute;
            height: 3px;
            background: linear-gradient(90deg, transparent, #CA8A04, transparent);
            transform-origin: left center;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.5s;
        }

        .route.active {
            opacity: 0.7;
            animation: flowAnimation 3s linear infinite;
        }

        @keyframes flowAnimation {
            0% { background-position: 0 0; }
            100% { background-position: 100px 0; }
        }

        .route.silk-road { background: linear-gradient(90deg, transparent, #CA8A04, transparent); }
        .route.maritime { background: linear-gradient(90deg, transparent, #3B82F6, transparent); }
        .route.tea-horse { background: linear-gradient(90deg, transparent, #10B981, transparent); }

        .goods-flow {
            position: absolute;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #FCD34D;
            box-shadow: 0 0 15px rgba(252, 211, 77, 0.8);
            opacity: 0;
            z-index: 5;
        }

        .goods-flow.active {
            animation: moveGoods 4s linear infinite;
            opacity: 1;
        }

        @keyframes moveGoods {
            0% { transform: translate(0, 0); opacity: 0; }
            10% { opacity: 1; }
            90% { opacity: 1; }
            100% { opacity: 0; }
        }

        .info-panel {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }

        .info-card {
            background: rgba(30, 41, 59, 0.8);
            padding: 25px;
            border-radius: 10px;
            border: 2px solid #334155;
            transition: all 0.3s;
        }

        .info-card:hover {
            border-color: #CA8A04;
            transform: translateY(-5px);
        }

        .info-card h2 {
            color: #CA8A04;
            margin-bottom: 15px;
            border-bottom: 2px solid #92400E;
            padding-bottom: 10px;
        }

        .goods-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
            gap: 10px;
            margin-top: 15px;
        }

        .goods-item {
            background: rgba(51, 65, 85, 0.5);
            padding: 12px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #475569;
            transition: all 0.3s;
        }

        .goods-item:hover {
            border-color: #CA8A04;
            transform: scale(1.05);
        }

        .goods-icon {
            font-size: 2em;
            margin-bottom: 5px;
        }

        .impact-item {
            background: rgba(51, 65, 85, 0.5);
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            border-left: 4px solid #CA8A04;
        }

        .impact-title {
            color: #FCD34D;
            font-weight: bold;
            margin-bottom: 8px;
            font-size: 1.1em;
        }

        .impact-desc {
            color: #CBD5E1;
            line-height: 1.6;
        }

        .legend {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 20px;
            flex-wrap: wrap;
            background: rgba(30, 41, 59, 0.6);
            padding: 15px;
            border-radius: 10px;
        }

        .legend-item {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .legend-line {
            width: 40px;
            height: 3px;
            border-radius: 2px;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }

        .stat-box {
            background: rgba(51, 65, 85, 0.5);
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border: 2px solid #475569;
        }

        .stat-number {
            font-size: 2.5em;
            color: #CA8A04;
            font-weight: bold;
            margin: 10px 0;
        }

        .stat-label {
            color: #94A3B8;
            font-size: 0.9em;
        }

        @media (max-width: 1024px) {
            .info-panel {
                grid-template-columns: 1fr;
            }
        }

        @media (max-width: 768px) {
            h1 {
                font-size: 1.8em;
            }

            #map {
                height: 400px;
            }

            .controls {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🗺️ 古代贸易路线</h1>
            <p class="subtitle">丝绸之路 · 海上丝绸之路 · 茶马古道 | 连接东西方文明的商路</p>
        </header>

        <div class="controls">
            <div class="control-group">
                <label>选择路线：</label>
                <button id="btnSilkRoad" onclick="toggleRoute('silk-road')">丝绸之路</button>
                <button id="btnMaritime" onclick="toggleRoute('maritime')">海上丝绸之路</button>
                <button id="btnTeaHorse" onclick="toggleRoute('tea-horse')">茶马古道</button>
            </div>

            <div class="control-group">
                <button onclick="toggleGoodsFlow()">商品流动动画</button>
                <button onclick="showAllRoutes()">显示所有路线</button>
                <button onclick="resetMap()">重置</button>
            </div>
        </div>

        <div class="map-container">
            <div id="map"></div>
            <div class="legend">
                <div class="legend-item">
                    <div class="legend-line" style="background: #CA8A04;"></div>
                    <span>丝绸之路（陆路）</span>
                </div>
                <div class="legend-item">
                    <div class="legend-line" style="background: #3B82F6;"></div>
                    <span>海上丝绸之路</span>
                </div>
                <div class="legend-item">
                    <div class="legend-line" style="background: #10B981;"></div>
                    <span>茶马古道</span>
                </div>
                <div class="legend-item">
                    <div style="width: 16px; height: 16px; background: #CA8A04; border: 2px solid #FCD34D; border-radius: 50%;"></div>
                    <span>贸易城市</span>
                </div>
            </div>
        </div>

        <div class="info-panel">
            <div class="info-card">
                <h2>📦 主要商品</h2>
                <div class="goods-list" id="goodsList">
                    <div class="goods-item">
                        <div class="goods-icon">🧵</div>
                        <div>丝绸</div>
                    </div>
                    <div class="goods-item">
                        <div class="goods-icon">🏺</div>
                        <div>瓷器</div>
                    </div>
                    <div class="goods-item">
                        <div class="goods-icon">🍵</div>
                        <div>茶叶</div>
                    </div>
                    <div class="goods-item">
                        <div class="goods-icon">🌿</div>
                        <div>香料</div>
                    </div>
                    <div class="goods-item">
                        <div class="goods-icon">💎</div>
                        <div>宝石</div>
                    </div>
                    <div class="goods-item">
                        <div class="goods-icon">🐴</div>
                        <div>马匹</div>
                    </div>
                    <div class="goods-item">
                        <div class="goods-icon">📜</div>
                        <div>纸张</div>
                    </div>
                    <div class="goods-item">
                        <div class="goods-icon">🔥</div>
                        <div>火药</div>
                    </div>
                </div>
                <div class="stats-grid">
                    <div class="stat-box">
                        <div class="stat-label">贸易城市</div>
                        <div class="stat-number" id="cityCount">0</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">路线总长</div>
                        <div class="stat-number" id="routeLength">0</div>
                        <div class="stat-label">公里</div>
                    </div>
                </div>
            </div>

            <div class="info-card">
                <h2>🌍 文化影响</h2>
                <div id="impactList">
                    <div class="impact-item">
                        <div class="impact-title">💱 经济繁荣</div>
                        <div class="impact-desc">促进了东西方的商品贸易，带动沿线城市经济发展，形成繁华的商业中心。</div>
                    </div>
                    <div class="impact-item">
                        <div class="impact-title">🎨 文化交流</div>
                        <div class="impact-desc">传播了中国的四大发明，引进了西域的音乐、艺术、宗教等文化元素。</div>
                    </div>
                    <div class="impact-item">
                        <div class="impact-title">🔬 技术传播</div>
                        <div class="impact-desc">丝绸、瓷器制作技术西传，阿拉伯数字、医学知识东传，促进技术进步。</div>
                    </div>
                    <div class="impact-item">
                        <div class="impact-title">🕌 宗教传播</div>
                        <div class="impact-desc">佛教、伊斯兰教、基督教等宗教沿丝绸之路传播，推动文明交流互鉴。</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const cities = [
            // Silk Road
            { id: 'xian', name: '长安', x: 65, y: 45, type: 'major', route: 'silk-road' },
            { id: 'dunhuang', name: '敦煌', x: 55, y: 42, route: 'silk-road' },
            { id: 'turfan', name: '吐鲁番', x: 48, y: 40, route: 'silk-road' },
            { id: 'samarkand', name: '撒马尔罕', x: 35, y: 38, type: 'major', route: 'silk-road' },
            { id: 'baghdad', name: '巴格达', x: 25, y: 42, type: 'major', route: 'silk-road' },
            { id: 'constantinople', name: '君士坦丁堡', x: 12, y: 35, type: 'major', route: 'silk-road' },

            // Maritime Silk Road
            { id: 'quanzhou', name: '泉州', x: 75, y: 52, type: 'major', route: 'maritime' },
            { id: 'guangzhou', name: '广州', x: 72, y: 55, type: 'major', route: 'maritime' },
            { id: 'hanoi', name: '河内', x: 68, y: 58, route: 'maritime' },
            { id: 'malacca', name: '马六甲', x: 60, y: 70, type: 'major', route: 'maritime' },
            { id: 'colombo', name: '科伦坡', x: 50, y: 75, route: 'maritime' },
            { id: 'calicut', name: '卡利卡特', x: 45, y: 72, route: 'maritime' },
            { id: 'hormuz', name: '霍尔木兹', x: 32, y: 62, route: 'maritime' },
            { id: 'aden', name: '亚丁', x: 25, y: 68, route: 'maritime' },

            // Tea Horse Road
            { id: 'chengdu', name: '成都', x: 68, y: 48, type: 'major', route: 'tea-horse' },
            { id: 'lhasa', name: '拉萨', x: 58, y: 50, type: 'major', route: 'tea-horse' },
            { id: 'lijiang', name: '丽江', x: 65, y: 52, route: 'tea-horse' },
            { id: 'dali', name: '大理', x: 64, y: 54, route: 'tea-horse' }
        ];

        const routes = [
            // Silk Road segments
            { from: 'xian', to: 'dunhuang', type: 'silk-road' },
            { from: 'dunhuang', to: 'turfan', type: 'silk-road' },
            { from: 'turfan', to: 'samarkand', type: 'silk-road' },
            { from: 'samarkand', to: 'baghdad', type: 'silk-road' },
            { from: 'baghdad', to: 'constantinople', type: 'silk-road' },

            // Maritime Silk Road segments
            { from: 'guangzhou', to: 'quanzhou', type: 'maritime' },
            { from: 'quanzhou', to: 'hanoi', type: 'maritime' },
            { from: 'hanoi', to: 'malacca', type: 'maritime' },
            { from: 'malacca', to: 'colombo', type: 'maritime' },
            { from: 'colombo', to: 'calicut', type: 'maritime' },
            { from: 'calicut', to: 'hormuz', type: 'maritime' },
            { from: 'hormuz', to: 'aden', type: 'maritime' },

            // Tea Horse Road segments
            { from: 'chengdu', to: 'lijiang', type: 'tea-horse' },
            { from: 'lijiang', to: 'dali', type: 'tea-horse' },
            { from: 'dali', to: 'lhasa', type: 'tea-horse' }
        ];

        let activeRoutes = new Set();
        let goodsFlowEnabled = false;

        function initMap() {
            const map = document.getElementById('map');
            map.innerHTML = '';

            // Draw routes
            routes.forEach((route, index) => {
                const fromCity = cities.find(c => c.id === route.from);
                const toCity = cities.find(c => c.id === route.to);

                if (!fromCity || !toCity) return;

                const x1 = (fromCity.x / 100) * map.offsetWidth;
                const y1 = (fromCity.y / 100) * map.offsetHeight;
                const x2 = (toCity.x / 100) * map.offsetWidth;
                const y2 = (toCity.y / 100) * map.offsetHeight;

                const length = Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
                const angle = Math.atan2(y2 - y1, x2 - x1) * (180 / Math.PI);

                const routeLine = document.createElement('div');
                routeLine.className = `route ${route.type}`;
                routeLine.id = `route-${index}`;
                routeLine.style.left = x1 + 'px';
                routeLine.style.top = y1 + 'px';
                routeLine.style.width = length + 'px';
                routeLine.style.transform = `rotate(${angle}deg)`;

                map.appendChild(routeLine);

                // Add goods flow animation
                if (goodsFlowEnabled) {
                    for (let i = 0; i < 3; i++) {
                        const goods = document.createElement('div');
                        goods.className = 'goods-flow';
                        goods.style.left = x1 + 'px';
                        goods.style.top = y1 + 'px';
                        goods.style.animationDelay = `${i * 1.3}s`;

                        const dx = x2 - x1;
                        const dy = y2 - y1;
                        goods.style.setProperty('--dx', dx + 'px');
                        goods.style.setProperty('--dy', dy + 'px');

                        map.appendChild(goods);

                        goods.style.animation = `moveGoods 4s linear infinite ${i * 1.3}s`;
                        goods.addEventListener('animationiteration', () => {
                            const progress = (Date.now() % 4000) / 4000;
                            goods.style.left = (x1 + dx * progress) + 'px';
                            goods.style.top = (y1 + dy * progress) + 'px';
                        });
                    }
                }
            });

            // Draw cities
            cities.forEach(city => {
                const cityDiv = document.createElement('div');
                cityDiv.className = `city ${city.type || ''}`;
                cityDiv.style.left = city.x + '%';
                cityDiv.style.top = city.y + '%';
                cityDiv.innerHTML = `<div class="city-label">${city.name}</div>`;
                cityDiv.onclick = () => showCityInfo(city);

                map.appendChild(cityDiv);
            });

            updateStats();
        }

        function toggleRoute(routeType) {
            const button = document.getElementById(`btn${routeType.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join('')}`);

            if (activeRoutes.has(routeType)) {
                activeRoutes.delete(routeType);
                button.classList.remove('active');
            } else {
                activeRoutes.add(routeType);
                button.classList.add('active');
            }

            updateRouteDisplay();
        }

        function updateRouteDisplay() {
            routes.forEach((route, index) => {
                const routeLine = document.getElementById(`route-${index}`);
                if (routeLine) {
                    if (activeRoutes.has(route.type)) {
                        routeLine.classList.add('active');
                    } else {
                        routeLine.classList.remove('active');
                    }
                }
            });

            // Update goods flow
            const allGoods = document.querySelectorAll('.goods-flow');
            allGoods.forEach(goods => {
                if (activeRoutes.size > 0 && goodsFlowEnabled) {
                    goods.classList.add('active');
                } else {
                    goods.classList.remove('active');
                }
            });
        }

        function toggleGoodsFlow() {
            goodsFlowEnabled = !goodsFlowEnabled;
            event.target.textContent = goodsFlowEnabled ? '停止商品流动' : '商品流动动画';
            initMap();
            updateRouteDisplay();
        }

        function showAllRoutes() {
            activeRoutes.clear();
            ['silk-road', 'maritime', 'tea-horse'].forEach(route => {
                activeRoutes.add(route);
                const btnId = `btn${route.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join('')}`;
                const button = document.getElementById(btnId);
                if (button) button.classList.add('active');
            });
            updateRouteDisplay();
        }

        function resetMap() {
            activeRoutes.clear();
            goodsFlowEnabled = false;
            document.querySelectorAll('.controls button').forEach(btn => {
                btn.classList.remove('active');
                if (btn.textContent.includes('商品流动')) {
                    btn.textContent = '商品流动动画';
                }
            });
            initMap();
        }

        function showCityInfo(city) {
            const routeInfo = {
                'silk-road': '丝绸之路上的重要节点，连接东西方贸易',
                'maritime': '海上丝绸之路的港口城市，海洋贸易枢纽',
                'tea-horse': '茶马古道上的贸易重镇，茶叶与马匹交换中心'
            };

            alert(`🏙️ ${city.name}\n\n类型: ${city.type === 'major' ? '主要城市' : '贸易节点'}\n路线: ${routeInfo[city.route] || '重要贸易城市'}`);
        }

        function updateStats() {
            document.getElementById('cityCount').textContent = cities.length;

            // Calculate approximate total route length
            let totalLength = 0;
            routes.forEach(route => {
                const fromCity = cities.find(c => c.id === route.from);
                const toCity = cities.find(c => c.id === route.to);
                if (fromCity && toCity) {
                    const dx = toCity.x - fromCity.x;
                    const dy = toCity.y - fromCity.y;
                    totalLength += Math.sqrt(dx * dx + dy * dy);
                }
            });

            document.getElementById('routeLength').textContent = Math.round(totalLength * 100);
        }

        // Initialize map on load
        window.addEventListener('load', initMap);
        window.addEventListener('resize', initMap);
    </script>
</body>
</html>$HTML$,
 75,
 0,
 685,
 false,
 0,
 NOW(),
 '{"name": "贸易路线", "description": "古代丝绸之路等重要贸易路线的地理分布和商品流动", "difficulty": "medium", "render_mode": "html"}');


-- [21/24] 朝代时间轴 (history, 75分)
INSERT INTO simulator_templates
(subject, topic, code, quality_score, visual_elements, line_count, has_setup_update, variable_count, created_at, metadata)
VALUES
('history',
 '朝代时间轴',
 $HTML$<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>中国历代王朝时间线 - 历史模拟器</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
            color: #F1F5F9;
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        header {
            text-align: center;
            margin-bottom: 30px;
            padding: 30px;
            background: rgba(146, 64, 14, 0.1);
            border-radius: 15px;
            border: 2px solid #92400E;
        }

        h1 {
            color: #CA8A04;
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 0 0 20px rgba(202, 138, 4, 0.5);
        }

        .subtitle {
            color: #94A3B8;
            font-size: 1.1em;
        }

        .controls {
            background: rgba(30, 41, 59, 0.8);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            align-items: center;
            border: 1px solid #334155;
        }

        .control-group {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        label {
            color: #CA8A04;
            font-weight: bold;
        }

        select, input[type="range"] {
            background: #334155;
            color: #F1F5F9;
            border: 1px solid #92400E;
            padding: 8px 12px;
            border-radius: 5px;
            cursor: pointer;
        }

        input[type="range"] {
            width: 200px;
        }

        button {
            background: linear-gradient(135deg, #92400E, #78350F);
            color: #F1F5F9;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(202, 138, 4, 0.3);
        }

        .timeline-container {
            background: rgba(30, 41, 59, 0.6);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            border: 2px solid #334155;
            overflow-x: auto;
        }

        .timeline {
            position: relative;
            min-height: 500px;
            padding: 20px 0;
        }

        .timeline-axis {
            position: absolute;
            bottom: 80px;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent, #CA8A04, transparent);
        }

        .dynasty-bar {
            position: absolute;
            bottom: 100px;
            height: 60px;
            background: linear-gradient(135deg, #92400E, #78350F);
            border: 2px solid #CA8A04;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            overflow: visible;
        }

        .dynasty-bar:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(202, 138, 4, 0.5);
            z-index: 10;
        }

        .dynasty-bar.selected {
            border-color: #FCD34D;
            box-shadow: 0 0 30px rgba(252, 211, 77, 0.6);
            z-index: 5;
        }

        .dynasty-label {
            font-size: 0.85em;
            text-align: center;
            padding: 0 3px;
            white-space: nowrap;
            overflow: visible;
            line-height: 1.2;
        }

        .year-marker {
            position: absolute;
            bottom: 50px;
            transform: translateX(-50%);
            text-align: center;
            font-size: 0.85em;
            color: #94A3B8;
        }

        .year-tick {
            width: 1px;
            height: 15px;
            background: #475569;
            margin: 0 auto 5px;
        }

        .event-marker {
            position: absolute;
            width: 12px;
            height: 12px;
            background: #CA8A04;
            border: 2px solid #FCD34D;
            border-radius: 50%;
            cursor: pointer;
            transition: all 0.3s;
            z-index: 20;
        }

        .event-marker:hover {
            transform: scale(1.5);
            box-shadow: 0 0 15px #FCD34D;
        }

        .event-label {
            position: absolute;
            bottom: 25px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(30, 41, 59, 0.95);
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 0.75em;
            white-space: nowrap;
            border: 1px solid #CA8A04;
            display: none;
        }

        .event-marker:hover .event-label {
            display: block;
        }

        .info-panel {
            background: rgba(30, 41, 59, 0.8);
            padding: 25px;
            border-radius: 10px;
            border: 2px solid #92400E;
            min-height: 200px;
        }

        .info-panel h2 {
            color: #CA8A04;
            margin-bottom: 15px;
            border-bottom: 2px solid #92400E;
            padding-bottom: 10px;
        }

        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }

        .info-item {
            background: rgba(51, 65, 85, 0.5);
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #CA8A04;
        }

        .info-label {
            color: #94A3B8;
            font-size: 0.9em;
            margin-bottom: 5px;
        }

        .info-value {
            color: #F1F5F9;
            font-size: 1.2em;
            font-weight: bold;
        }

        .stats-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }

        .stat-card {
            background: rgba(30, 41, 59, 0.8);
            padding: 20px;
            border-radius: 10px;
            border: 2px solid #334155;
            text-align: center;
            transition: all 0.3s;
        }

        .stat-card:hover {
            border-color: #CA8A04;
            transform: translateY(-5px);
        }

        .stat-number {
            font-size: 2.5em;
            color: #CA8A04;
            font-weight: bold;
            margin: 10px 0;
        }

        .stat-label {
            color: #94A3B8;
        }

        .comparison-bars {
            margin-top: 20px;
        }

        .comparison-item {
            margin-bottom: 15px;
        }

        .comparison-label {
            display: flex;
            justify-content: space-between;
            margin-bottom: 5px;
            font-size: 0.9em;
        }

        .comparison-bar {
            height: 25px;
            background: rgba(51, 65, 85, 0.5);
            border-radius: 5px;
            overflow: hidden;
            position: relative;
        }

        .comparison-fill {
            height: 100%;
            background: linear-gradient(90deg, #92400E, #CA8A04);
            border-radius: 5px;
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 10px;
            font-size: 0.85em;
            font-weight: bold;
        }

        .legend {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 20px;
            flex-wrap: wrap;
        }

        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
            background: rgba(30, 41, 59, 0.6);
            padding: 8px 15px;
            border-radius: 5px;
        }

        .legend-color {
            width: 20px;
            height: 20px;
            border-radius: 3px;
            border: 2px solid #CA8A04;
        }

        @media (max-width: 768px) {
            h1 {
                font-size: 1.8em;
            }

            .controls {
                flex-direction: column;
            }

            .info-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🏛️ 中国历代王朝时间线</h1>
            <p class="subtitle">探索中国五千年文明史 | 朝代更替 · 历史传承</p>
        </header>

        <div class="controls">
            <div class="control-group">
                <label>时期筛选：</label>
                <select id="periodFilter">
                    <option value="all">全部朝代</option>
                    <option value="ancient">上古至秦汉</option>
                    <option value="medieval">魏晋南北朝至隋唐</option>
                    <option value="late">宋元明清</option>
                </select>
            </div>

            <div class="control-group">
                <label>时间缩放：</label>
                <input type="range" id="zoomSlider" min="0.5" max="2" step="0.1" value="1">
                <span id="zoomValue">100%</span>
            </div>

            <div class="control-group">
                <button onclick="showEvents()">显示重大事件</button>
                <button onclick="compareDurations()">朝代时长对比</button>
                <button onclick="resetView()">重置视图</button>
            </div>
        </div>

        <div class="timeline-container">
            <div class="timeline" id="timeline"></div>
        </div>

        <div class="info-panel" id="infoPanel">
            <h2>王朝信息</h2>
            <p style="color: #94A3B8;">点击时间线上的朝代查看详细信息</p>
        </div>

        <div class="stats-container">
            <div class="stat-card">
                <div class="stat-label">统计朝代数</div>
                <div class="stat-number" id="totalDynasties">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">历史跨度</div>
                <div class="stat-number" id="timeSpan">0</div>
                <div class="stat-label">年</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">最长王朝</div>
                <div class="stat-number" id="longestDynasty">-</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">平均国祚</div>
                <div class="stat-number" id="avgDuration">0</div>
                <div class="stat-label">年</div>
            </div>
        </div>
    </div>

    <script>
        const dynasties = [
            { name: '夏', start: -2070, end: -1600, founder: '禹', capital: '阳城', events: [{year: -2070, desc: '大禹建立夏朝'}] },
            { name: '商', start: -1600, end: -1046, founder: '汤', capital: '亳', events: [{year: -1600, desc: '商汤灭夏'}, {year: -1300, desc: '盘庚迁殷'}] },
            { name: '周', start: -1046, end: -256, founder: '武王', capital: '镐京', events: [{year: -1046, desc: '武王伐纣'}, {year: -770, desc: '平王东迁'}] },
            { name: '秦', start: -221, end: -206, founder: '嬴政', capital: '咸阳', events: [{year: -221, desc: '秦始皇统一六国'}, {year: -210, desc: '秦始皇去世'}] },
            { name: '汉', start: -202, end: 220, founder: '刘邦', capital: '长安', events: [{year: -202, desc: '刘邦建汉'}, {year: 8, desc: '王莽篡汉'}, {year: 25, desc: '光武中兴'}] },
            { name: '三国', start: 220, end: 280, founder: '魏蜀吴', capital: '洛阳/成都/建业', events: [{year: 220, desc: '曹丕称帝'}, {year: 263, desc: '蜀汉灭亡'}] },
            { name: '晋', start: 266, end: 420, founder: '司马炎', capital: '洛阳', events: [{year: 280, desc: '西晋统一'}, {year: 316, desc: '西晋灭亡'}] },
            { name: '南北朝', start: 420, end: 589, founder: '多政权', capital: '建康/平城', events: [{year: 439, desc: '北魏统一北方'}] },
            { name: '隋', start: 581, end: 618, founder: '杨坚', capital: '大兴', events: [{year: 589, desc: '隋灭陈统一'}, {year: 605, desc: '开凿大运河'}] },
            { name: '唐', start: 618, end: 907, founder: '李渊', capital: '长安', events: [{year: 626, desc: '玄武门之变'}, {year: 755, desc: '安史之乱'}] },
            { name: '五代十国', start: 907, end: 960, founder: '多政权', capital: '汴梁等', events: [{year: 907, desc: '朱温建后梁'}] },
            { name: '宋', start: 960, end: 1279, founder: '赵匡胤', capital: '开封/临安', events: [{year: 960, desc: '陈桥兵变'}, {year: 1127, desc: '靖康之变'}] },
            { name: '元', start: 1271, end: 1368, founder: '忽必烈', capital: '大都', events: [{year: 1271, desc: '忽必烈建元'}, {year: 1279, desc: '崖山海战'}] },
            { name: '明', start: 1368, end: 1644, founder: '朱元璋', capital: '南京/北京', events: [{year: 1368, desc: '朱元璋称帝'}, {year: 1421, desc: '迁都北京'}] },
            { name: '清', start: 1644, end: 1912, founder: '皇太极', capital: '北京', events: [{year: 1644, desc: '入关定鼎'}, {year: 1840, desc: '鸦片战争'}, {year: 1911, desc: '辛亥革命'}] }
        ];

        let currentZoom = 1;
        let showEventsFlag = false;
        let selectedDynasty = null;

        function initTimeline() {
            const minYear = Math.min(...dynasties.map(d => d.start));
            const maxYear = Math.max(...dynasties.map(d => d.end));
            const totalYears = maxYear - minYear;

            const timeline = document.getElementById('timeline');
            timeline.innerHTML = '';

            // Add year markers
            const markerInterval = Math.ceil(totalYears / 15);
            for (let year = Math.ceil(minYear / markerInterval) * markerInterval; year <= maxYear; year += markerInterval) {
                const position = ((year - minYear) / totalYears) * 100;
                const marker = document.createElement('div');
                marker.className = 'year-marker';
                marker.style.left = position + '%';
                marker.innerHTML = `<div class="year-tick"></div>${year > 0 ? year : Math.abs(year) + '前'}`;
                timeline.appendChild(marker);
            }

            // Add timeline axis
            const axis = document.createElement('div');
            axis.className = 'timeline-axis';
            timeline.appendChild(axis);

            // Add dynasties
            dynasties.forEach((dynasty, index) => {
                const duration = dynasty.end - dynasty.start;
                const startPos = ((dynasty.start - minYear) / totalYears) * 100;
                const width = (duration / totalYears) * 100;

                const bar = document.createElement('div');
                bar.className = 'dynasty-bar';
                bar.style.left = startPos + '%';
                bar.style.width = width + '%';
                bar.innerHTML = `<div class="dynasty-label">${dynasty.name} (${duration}年)</div>`;
                bar.onclick = () => selectDynasty(dynasty);

                // Alternate heights for better visibility
                bar.style.bottom = (100 + (index % 3) * 70) + 'px';

                timeline.appendChild(bar);

                // Add events if enabled
                if (showEventsFlag) {
                    dynasty.events.forEach(event => {
                        const eventPos = ((event.year - minYear) / totalYears) * 100;
                        const eventMarker = document.createElement('div');
                        eventMarker.className = 'event-marker';
                        eventMarker.style.left = eventPos + '%';
                        eventMarker.style.bottom = (90 + (index % 3) * 70) + 'px';
                        eventMarker.innerHTML = `<div class="event-label">${event.desc}</div>`;
                        timeline.appendChild(eventMarker);
                    });
                }
            });

            updateStats();
        }

        function selectDynasty(dynasty) {
            selectedDynasty = dynasty;

            // Update visual selection
            document.querySelectorAll('.dynasty-bar').forEach(bar => {
                bar.classList.remove('selected');
            });
            event.target.classList.add('selected');

            // Update info panel
            const duration = dynasty.end - dynasty.start;
            const infoPanel = document.getElementById('infoPanel');
            // 特殊时期不加"朝"字
            const specialPeriods = ['三国', '南北朝', '五代十国'];
            const title = specialPeriods.includes(dynasty.name) ? dynasty.name : dynasty.name + '朝';
            infoPanel.innerHTML = `
                <h2>${title} (${dynasty.start > 0 ? dynasty.start : Math.abs(dynasty.start) + '前'} - ${dynasty.end > 0 ? dynasty.end : Math.abs(dynasty.end) + '前'})</h2>
                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-label">开国君主</div>
                        <div class="info-value">${dynasty.founder}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">都城</div>
                        <div class="info-value">${dynasty.capital}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">国祚</div>
                        <div class="info-value">${duration} 年</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">重大事件</div>
                        <div class="info-value">${dynasty.events.length} 项</div>
                    </div>
                </div>
                <div class="comparison-bars">
                    <h3 style="color: #CA8A04; margin-bottom: 15px;">历史地位对比</h3>
                    ${dynasty.events.map(event => `
                        <div class="comparison-item">
                            <div class="comparison-label">
                                <span>${event.desc}</span>
                                <span>${event.year > 0 ? event.year : Math.abs(event.year) + '前'}年</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        }

        function updateStats() {
            const totalDynasties = dynasties.length;
            const minYear = Math.min(...dynasties.map(d => d.start));
            const maxYear = Math.max(...dynasties.map(d => d.end));
            const timeSpan = maxYear - minYear;

            const durations = dynasties.map(d => ({name: d.name, duration: d.end - d.start}));
            const longest = durations.reduce((max, d) => d.duration > max.duration ? d : max);
            const avgDuration = Math.round(durations.reduce((sum, d) => sum + d.duration, 0) / totalDynasties);

            document.getElementById('totalDynasties').textContent = totalDynasties;
            document.getElementById('timeSpan').textContent = timeSpan;
            document.getElementById('longestDynasty').textContent = longest.name;
            document.getElementById('avgDuration').textContent = avgDuration;
        }

        function showEvents() {
            showEventsFlag = !showEventsFlag;
            initTimeline();
            event.target.textContent = showEventsFlag ? '隐藏事件' : '显示重大事件';
        }

        function compareDurations() {
            const durations = dynasties.map(d => ({
                name: d.name,
                duration: d.end - d.start
            })).sort((a, b) => b.duration - a.duration);

            const maxDuration = durations[0].duration;

            const infoPanel = document.getElementById('infoPanel');
            infoPanel.innerHTML = `
                <h2>📊 朝代国祚时长对比</h2>
                <div class="comparison-bars">
                    ${durations.map((d, index) => `
                        <div class="comparison-item">
                            <div class="comparison-label">
                                <span>${index + 1}. ${d.name}</span>
                                <span>${d.duration} 年</span>
                            </div>
                            <div class="comparison-bar">
                                <div class="comparison-fill" style="width: ${(d.duration / maxDuration) * 100}%">
                                    ${Math.round((d.duration / maxDuration) * 100)}%
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        }

        function resetView() {
            currentZoom = 1;
            showEventsFlag = false;
            selectedDynasty = null;
            document.getElementById('zoomSlider').value = 1;
            document.getElementById('zoomValue').textContent = '100%';
            document.getElementById('periodFilter').value = 'all';
            initTimeline();

            const infoPanel = document.getElementById('infoPanel');
            infoPanel.innerHTML = `
                <h2>王朝信息</h2>
                <p style="color: #94A3B8;">点击时间线上的朝代查看详细信息</p>
            `;
        }

        // Event listeners
        document.getElementById('zoomSlider').addEventListener('input', (e) => {
            currentZoom = parseFloat(e.target.value);
            document.getElementById('zoomValue').textContent = Math.round(currentZoom * 100) + '%';
            document.querySelector('.timeline').style.transform = `scaleX(${currentZoom})`;
        });

        document.getElementById('periodFilter').addEventListener('change', (e) => {
            const filter = e.target.value;
            const bars = document.querySelectorAll('.dynasty-bar');

            bars.forEach((bar, index) => {
                const dynasty = dynasties[index];
                let show = true;

                if (filter === 'ancient') {
                    show = dynasty.end < 220;
                } else if (filter === 'medieval') {
                    show = dynasty.start >= 220 && dynasty.end < 960;
                } else if (filter === 'late') {
                    show = dynasty.start >= 960;
                }

                bar.style.opacity = show ? '1' : '0.2';
                bar.style.pointerEvents = show ? 'auto' : 'none';
            });
        });

        // Initialize
        initTimeline();
    </script>
</body>
</html>$HTML$,
 75,
 0,
 651,
 false,
 0,
 NOW(),
 '{"name": "朝代时间轴", "description": "中国历史朝代更替的时间线和重要事件", "difficulty": "easy", "render_mode": "html"}');


-- [22/24] 水循环 (geography, 75分)
INSERT INTO simulator_templates
(subject, topic, code, quality_score, visual_elements, line_count, has_setup_update, variable_count, created_at, metadata)
VALUES
('geography',
 '水循环',
 $HTML$<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>水循环模拟器 - 地理学</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
            color: #F1F5F9;
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(14, 165, 233, 0.1);
            border-radius: 12px;
            border: 1px solid rgba(14, 165, 233, 0.3);
        }

        h1 {
            font-size: 2.5em;
            color: #0EA5E9;
            margin-bottom: 10px;
        }

        .subtitle {
            font-size: 1.1em;
            color: #94A3B8;
        }

        .main-content {
            display: grid;
            grid-template-columns: 1fr 350px;
            gap: 20px;
            margin-bottom: 20px;
        }

        .canvas-container {
            background: rgba(15, 23, 42, 0.6);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(14, 165, 233, 0.3);
        }

        canvas {
            width: 100%;
            height: 600px;
            border-radius: 8px;
            background: linear-gradient(180deg, #87CEEB 0%, #E0F2FE 50%, #10B981 100%);
            display: block;
        }

        .controls-panel {
            background: rgba(15, 23, 42, 0.6);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(14, 165, 233, 0.3);
        }

        .control-group {
            margin-bottom: 25px;
        }

        .control-group h3 {
            color: #0EA5E9;
            margin-bottom: 12px;
            font-size: 1.1em;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .control-group h3::before {
            content: '▶';
            font-size: 0.8em;
        }

        button {
            width: 100%;
            padding: 12px;
            margin: 6px 0;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 500;
        }

        .btn-primary {
            background: #0EA5E9;
            color: white;
        }

        .btn-primary:hover {
            background: #0284C7;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(14, 165, 233, 0.4);
        }

        .btn-secondary {
            background: #10B981;
            color: white;
        }

        .btn-secondary:hover {
            background: #059669;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
        }

        .btn-accent {
            background: #F59E0B;
            color: white;
        }

        .btn-accent:hover {
            background: #D97706;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(245, 158, 11, 0.4);
        }

        .slider-control {
            margin: 15px 0;
        }

        .slider-control label {
            display: block;
            margin-bottom: 8px;
            color: #94A3B8;
            font-size: 0.9em;
        }

        input[type="range"] {
            width: 100%;
            height: 6px;
            border-radius: 3px;
            background: rgba(148, 163, 184, 0.2);
            outline: none;
            -webkit-appearance: none;
        }

        input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: #0EA5E9;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        input[type="range"]::-webkit-slider-thumb:hover {
            background: #0284C7;
            transform: scale(1.2);
        }

        .value-display {
            display: inline-block;
            background: rgba(14, 165, 233, 0.2);
            padding: 4px 12px;
            border-radius: 6px;
            font-weight: 600;
            color: #0EA5E9;
            float: right;
        }

        .info-panel {
            background: rgba(15, 23, 42, 0.6);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(14, 165, 233, 0.3);
        }

        .info-panel h3 {
            color: #0EA5E9;
            margin-bottom: 15px;
            font-size: 1.2em;
        }

        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }

        .info-card {
            background: rgba(14, 165, 233, 0.1);
            padding: 15px;
            border-radius: 8px;
            border: 1px solid rgba(14, 165, 233, 0.2);
        }

        .info-card h4 {
            color: #10B981;
            font-size: 0.9em;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .info-card p {
            font-size: 1.4em;
            font-weight: 600;
            color: #F1F5F9;
        }

        .legend {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin-top: 15px;
        }

        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .legend-color {
            width: 24px;
            height: 24px;
            border-radius: 4px;
            border: 2px solid rgba(241, 245, 249, 0.3);
        }

        .legend-label {
            font-size: 0.9em;
            color: #CBD5E1;
        }

        .phase-display {
            background: rgba(14, 165, 233, 0.15);
            padding: 12px;
            border-radius: 8px;
            margin: 10px 0;
            border-left: 4px solid #0EA5E9;
        }

        .phase-display p {
            font-size: 0.95em;
            line-height: 1.6;
            color: #CBD5E1;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }

        .active-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #10B981;
            margin-left: 8px;
            animation: pulse 2s ease-in-out infinite;
        }

        @media (max-width: 1024px) {
            .main-content {
                grid-template-columns: 1fr;
            }

            .info-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>💧 水循环模拟器</h1>
            <p class="subtitle">探索地球水的三态变化与能量交换过程</p>
        </header>

        <div class="main-content">
            <div class="canvas-container">
                <canvas id="simulatorCanvas"></canvas>
            </div>

            <div class="controls-panel">
                <div class="control-group">
                    <h3>环境控制</h3>
                    <button class="btn-primary" onclick="increaseTemperature()">🌡️ 升高温度</button>
                    <button class="btn-secondary" onclick="decreaseTemperature()">❄️ 降低温度</button>
                    <button class="btn-accent" onclick="addSunEnergy()">☀️ 增加太阳辐射</button>
                </div>

                <div class="control-group">
                    <h3>水循环过程</h3>
                    <button class="btn-primary" onclick="triggerEvaporation()">💨 强化蒸发</button>
                    <button class="btn-secondary" onclick="triggerPrecipitation()">🌧️ 触发降水</button>
                    <button class="btn-accent" onclick="triggerRunoff()">🌊 增加径流</button>
                </div>

                <div class="control-group">
                    <h3>模拟控制</h3>
                    <button class="btn-secondary" onclick="toggleSimulation()">▶️ 开始/暂停</button>
                    <button class="btn-primary" onclick="resetSimulation()">🔄 重置</button>
                </div>

                <div class="control-group">
                    <h3>参数调节</h3>
                    <div class="slider-control">
                        <label>
                            风速
                            <span class="value-display" id="windValue">5 m/s</span>
                        </label>
                        <input type="range" id="windSlider" min="0" max="20" step="1" value="5">
                    </div>
                    <div class="slider-control">
                        <label>
                            湿度
                            <span class="value-display" id="humidityValue">60%</span>
                        </label>
                        <input type="range" id="humiditySlider" min="0" max="100" step="5" value="60">
                    </div>
                </div>

                <div class="phase-display">
                    <p><strong>当前阶段：</strong><span id="currentPhase">蒸发</span></p>
                    <p><strong>水的状态：</strong><span id="waterState">液态</span></p>
                </div>

                <div class="legend">
                    <div class="legend-item">
                        <div class="legend-color" style="background: #3B82F6;"></div>
                        <span class="legend-label">液态水</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #E0F2FE;"></div>
                        <span class="legend-label">水蒸气</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #FFFFFF;"></div>
                        <span class="legend-label">冰晶</span>
                    </div>
                </div>
            </div>
        </div>

        <div class="info-panel">
            <h3>水循环统计 <span class="active-indicator"></span></h3>
            <div class="info-grid">
                <div class="info-card">
                    <h4>温度</h4>
                    <p id="tempDisplay">25°C</p>
                </div>
                <div class="info-card">
                    <h4>蒸发量</h4>
                    <p id="evapDisplay">0 m³</p>
                </div>
                <div class="info-card">
                    <h4>降水量</h4>
                    <p id="precipDisplay">0 mm</p>
                </div>
                <div class="info-card">
                    <h4>径流量</h4>
                    <p id="runoffDisplay">0 m³</p>
                </div>
                <div class="info-card">
                    <h4>云层覆盖</h4>
                    <p id="cloudDisplay">0%</p>
                </div>
                <div class="info-card">
                    <h4>能量交换</h4>
                    <p id="energyDisplay">0 kJ</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('simulatorCanvas');
        const ctx = canvas.getContext('2d');

        // 设置canvas实际分辨率
        function resizeCanvas() {
            const rect = canvas.getBoundingClientRect();
            canvas.width = rect.width * window.devicePixelRatio;
            canvas.height = rect.height * window.devicePixelRatio;
            ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
        }
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);

        // 模拟状态
        let state = {
            running: false,
            temperature: 25,
            windSpeed: 5,
            humidity: 60,
            evaporation: 0,
            precipitation: 0,
            runoff: 0,
            energy: 0,
            waterParticles: [],
            vaporParticles: [],
            clouds: [],
            raindrops: [],
            rivers: [],
            sun: { x: 100, y: 80, intensity: 1 }
        };

        // 初始化水体
        function initWater() {
            const w = canvas.getBoundingClientRect().width;
            const h = canvas.getBoundingClientRect().height;

            // 海洋/湖泊
            for(let i = 0; i < 200; i++) {
                state.waterParticles.push({
                    x: Math.random() * w,
                    y: h * 0.75 + Math.random() * h * 0.2,
                    vx: (Math.random() - 0.5) * 0.5,
                    vy: (Math.random() - 0.5) * 0.5,
                    radius: 2 + Math.random() * 3,
                    phase: 'liquid'
                });
            }
        }

        // 温度控制
        function increaseTemperature() {
            state.temperature = Math.min(40, state.temperature + 5);
            updateDisplay();
        }

        function decreaseTemperature() {
            state.temperature = Math.max(-10, state.temperature - 5);
            updateDisplay();
        }

        function addSunEnergy() {
            state.sun.intensity = Math.min(2, state.sun.intensity + 0.2);
            state.energy += 100;
            updateDisplay();
        }

        // 水循环过程
        function triggerEvaporation() {
            const w = canvas.getBoundingClientRect().width;
            const h = canvas.getBoundingClientRect().height;

            for(let i = 0; i < 20; i++) {
                state.vaporParticles.push({
                    x: Math.random() * w,
                    y: h * 0.75,
                    vx: (Math.random() - 0.5) * 2,
                    vy: -2 - Math.random() * 2,
                    radius: 3 + Math.random() * 4,
                    alpha: 0.6,
                    phase: 'vapor'
                });
            }
            state.evaporation += 10;
            state.energy += 50;
            updateDisplay();
        }

        function triggerPrecipitation() {
            const w = canvas.getBoundingClientRect().width;
            const h = canvas.getBoundingClientRect().height;

            for(let i = 0; i < 30; i++) {
                state.raindrops.push({
                    x: Math.random() * w,
                    y: h * 0.3 + Math.random() * 50,
                    vx: state.windSpeed * 0.3,
                    vy: 5 + Math.random() * 3,
                    length: 10 + Math.random() * 10,
                    alpha: 0.8
                });
            }
            state.precipitation += 5;
            state.energy -= 30;
            updateDisplay();
        }

        function triggerRunoff() {
            const w = canvas.getBoundingClientRect().width;
            const h = canvas.getBoundingClientRect().height;

            state.rivers.push({
                x: w * 0.2 + Math.random() * w * 0.6,
                y: h * 0.65,
                particles: [],
                life: 0
            });

            state.runoff += 15;
            updateDisplay();
        }

        // 切换模拟
        function toggleSimulation() {
            state.running = !state.running;
            if(state.running && state.waterParticles.length === 0) {
                initWater();
            }
        }

        // 重置模拟
        function resetSimulation() {
            state = {
                running: false,
                temperature: 25,
                windSpeed: state.windSpeed,
                humidity: state.humidity,
                evaporation: 0,
                precipitation: 0,
                runoff: 0,
                energy: 0,
                waterParticles: [],
                vaporParticles: [],
                clouds: [],
                raindrops: [],
                rivers: [],
                sun: { x: 100, y: 80, intensity: 1 }
            };
            updateDisplay();
        }

        // 更新物理
        function updatePhysics() {
            if(!state.running) return;

            const w = canvas.getBoundingClientRect().width;
            const h = canvas.getBoundingClientRect().height;

            // 自动蒸发（温度影响）
            if(Math.random() < 0.02 * (state.temperature / 25) * state.sun.intensity) {
                state.vaporParticles.push({
                    x: Math.random() * w,
                    y: h * 0.75 + Math.random() * 20,
                    vx: (Math.random() - 0.5) * state.windSpeed * 0.2,
                    vy: -1 - Math.random() * 2,
                    radius: 2 + Math.random() * 3,
                    alpha: 0.4,
                    phase: 'vapor'
                });
                state.evaporation += 0.5;
            }

            // 更新水蒸气
            state.vaporParticles = state.vaporParticles.filter(p => {
                p.x += p.vx;
                p.y += p.vy;
                p.alpha -= 0.005;

                // 凝结成云
                if(p.y < h * 0.35 && Math.random() < 0.02) {
                    state.clouds.push({
                        x: p.x,
                        y: p.y,
                        radius: 20 + Math.random() * 30,
                        alpha: 0.7,
                        vx: state.windSpeed * 0.1
                    });
                    return false;
                }

                return p.alpha > 0 && p.y > 0;
            });

            // 更新云层
            state.clouds = state.clouds.filter(c => {
                c.x += c.vx;
                c.alpha -= 0.001;

                // 降水
                if(c.alpha > 0.5 && Math.random() < 0.01) {
                    for(let i = 0; i < 3; i++) {
                        state.raindrops.push({
                            x: c.x + (Math.random() - 0.5) * c.radius,
                            y: c.y,
                            vx: state.windSpeed * 0.2,
                            vy: 4 + Math.random() * 2,
                            length: 8 + Math.random() * 8,
                            alpha: 0.7
                        });
                    }
                    state.precipitation += 0.2;
                }

                // 云层循环
                if(c.x > w + c.radius) c.x = -c.radius;
                if(c.x < -c.radius) c.x = w + c.radius;

                return c.alpha > 0.1;
            });

            // 更新雨滴
            state.raindrops = state.raindrops.filter(r => {
                r.x += r.vx;
                r.y += r.vy;
                r.alpha -= 0.01;

                // 落到地面
                if(r.y > h * 0.75) {
                    state.runoff += 0.1;
                    return false;
                }

                return r.alpha > 0;
            });

            // 更新河流
            state.rivers.forEach(river => {
                river.life++;
                if(river.life < 60 && river.life % 2 === 0) {
                    river.particles.push({
                        x: river.x,
                        y: river.y,
                        vx: 2 + Math.random(),
                        vy: 1 + Math.random() * 0.5,
                        radius: 2 + Math.random() * 2,
                        alpha: 0.8
                    });
                }

                river.particles.forEach(p => {
                    p.x += p.vx;
                    p.y += p.vy;
                    p.alpha -= 0.01;
                });

                river.particles = river.particles.filter(p => p.alpha > 0 && p.y < h);
            });

            state.rivers = state.rivers.filter(r => r.life < 100);

            // 更新显示
            updateDisplay();
        }

        // 更新显示数据
        function updateDisplay() {
            document.getElementById('tempDisplay').textContent = state.temperature + '°C';
            document.getElementById('evapDisplay').textContent = Math.floor(state.evaporation) + ' m³';
            document.getElementById('precipDisplay').textContent = Math.floor(state.precipitation) + ' mm';
            document.getElementById('runoffDisplay').textContent = Math.floor(state.runoff) + ' m³';
            document.getElementById('cloudDisplay').textContent = Math.floor((state.clouds.length / 50) * 100) + '%';
            document.getElementById('energyDisplay').textContent = Math.floor(state.energy) + ' kJ';

            // 更新当前阶段
            if(state.vaporParticles.length > state.clouds.length && state.vaporParticles.length > state.raindrops.length) {
                document.getElementById('currentPhase').textContent = '蒸发';
                document.getElementById('waterState').textContent = '气态';
            } else if(state.clouds.length > state.raindrops.length) {
                document.getElementById('currentPhase').textContent = '凝结';
                document.getElementById('waterState').textContent = '液态微滴';
            } else if(state.raindrops.length > 0) {
                document.getElementById('currentPhase').textContent = '降水';
                document.getElementById('waterState').textContent = '液态';
            } else {
                document.getElementById('currentPhase').textContent = '径流';
                document.getElementById('waterState').textContent = '液态';
            }
        }

        // 渲染
        function render() {
            const w = canvas.getBoundingClientRect().width;
            const h = canvas.getBoundingClientRect().height;

            // 天空渐变
            const skyGradient = ctx.createLinearGradient(0, 0, 0, h * 0.6);
            skyGradient.addColorStop(0, '#87CEEB');
            skyGradient.addColorStop(1, '#E0F2FE');
            ctx.fillStyle = skyGradient;
            ctx.fillRect(0, 0, w, h * 0.6);

            // 绘制太阳
            ctx.globalAlpha = state.sun.intensity;
            const sunGradient = ctx.createRadialGradient(
                state.sun.x, state.sun.y, 0,
                state.sun.x, state.sun.y, 40
            );
            sunGradient.addColorStop(0, '#FCD34D');
            sunGradient.addColorStop(0.5, '#F59E0B');
            sunGradient.addColorStop(1, 'rgba(245, 158, 11, 0)');
            ctx.fillStyle = sunGradient;
            ctx.beginPath();
            ctx.arc(state.sun.x, state.sun.y, 40, 0, Math.PI * 2);
            ctx.fill();

            // 太阳光线
            ctx.strokeStyle = 'rgba(252, 211, 77, 0.4)';
            ctx.lineWidth = 2;
            for(let i = 0; i < 12; i++) {
                const angle = (i / 12) * Math.PI * 2;
                ctx.beginPath();
                ctx.moveTo(
                    state.sun.x + Math.cos(angle) * 50,
                    state.sun.y + Math.sin(angle) * 50
                );
                ctx.lineTo(
                    state.sun.x + Math.cos(angle) * 70,
                    state.sun.y + Math.sin(angle) * 70
                );
                ctx.stroke();
            }
            ctx.globalAlpha = 1;

            // 绘制云层
            state.clouds.forEach(cloud => {
                ctx.globalAlpha = cloud.alpha;
                const cloudGradient = ctx.createRadialGradient(
                    cloud.x, cloud.y, 0,
                    cloud.x, cloud.y, cloud.radius
                );
                cloudGradient.addColorStop(0, '#FFFFFF');
                cloudGradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
                ctx.fillStyle = cloudGradient;

                // 绘制多个圆形组成云朵
                for(let i = 0; i < 5; i++) {
                    ctx.beginPath();
                    ctx.arc(
                        cloud.x + (i - 2) * cloud.radius * 0.3,
                        cloud.y + Math.sin(i) * cloud.radius * 0.2,
                        cloud.radius * 0.6,
                        0, Math.PI * 2
                    );
                    ctx.fill();
                }
            });
            ctx.globalAlpha = 1;

            // 绘制水蒸气
            state.vaporParticles.forEach(p => {
                ctx.globalAlpha = p.alpha;
                const gradient = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.radius);
                gradient.addColorStop(0, '#E0F2FE');
                gradient.addColorStop(1, 'rgba(224, 242, 254, 0)');
                ctx.fillStyle = gradient;
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                ctx.fill();
            });
            ctx.globalAlpha = 1;

            // 绘制雨滴
            state.raindrops.forEach(r => {
                ctx.globalAlpha = r.alpha;
                ctx.strokeStyle = '#3B82F6';
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.moveTo(r.x, r.y);
                ctx.lineTo(r.x + r.vx * 2, r.y + r.length);
                ctx.stroke();
            });
            ctx.globalAlpha = 1;

            // 地面
            const groundGradient = ctx.createLinearGradient(0, h * 0.6, 0, h);
            groundGradient.addColorStop(0, '#10B981');
            groundGradient.addColorStop(0.5, '#059669');
            groundGradient.addColorStop(1, '#047857');
            ctx.fillStyle = groundGradient;
            ctx.fillRect(0, h * 0.6, w, h * 0.15);

            // 水体（海洋/湖泊）
            const waterGradient = ctx.createLinearGradient(0, h * 0.75, 0, h);
            waterGradient.addColorStop(0, '#3B82F6');
            waterGradient.addColorStop(1, '#1E40AF');
            ctx.fillStyle = waterGradient;
            ctx.fillRect(0, h * 0.75, w, h * 0.25);

            // 绘制水波纹
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
            ctx.lineWidth = 2;
            for(let i = 0; i < 5; i++) {
                ctx.beginPath();
                ctx.moveTo(0, h * 0.75 + i * 15);
                for(let x = 0; x < w; x += 20) {
                    ctx.lineTo(x, h * 0.75 + i * 15 + Math.sin(x * 0.05 + Date.now() * 0.001) * 3);
                }
                ctx.stroke();
            }

            // 绘制水分子
            state.waterParticles.forEach(p => {
                ctx.fillStyle = 'rgba(59, 130, 246, 0.8)';
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                ctx.fill();
            });

            // 绘制河流径流
            state.rivers.forEach(river => {
                river.particles.forEach(p => {
                    ctx.globalAlpha = p.alpha;
                    ctx.fillStyle = '#3B82F6';
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                    ctx.fill();
                });
            });
            ctx.globalAlpha = 1;

            // 绘制能量指示箭头（蒸发过程）
            if(state.vaporParticles.length > 0) {
                ctx.strokeStyle = '#F59E0B';
                ctx.fillStyle = '#F59E0B';
                ctx.lineWidth = 3;

                for(let i = 0; i < 3; i++) {
                    const x = w * (0.3 + i * 0.2);
                    const y1 = h * 0.75;
                    const y2 = h * 0.45;

                    ctx.beginPath();
                    ctx.moveTo(x, y1);
                    ctx.lineTo(x, y2);
                    ctx.stroke();

                    // 箭头
                    ctx.beginPath();
                    ctx.moveTo(x, y2);
                    ctx.lineTo(x - 8, y2 + 15);
                    ctx.lineTo(x + 8, y2 + 15);
                    ctx.closePath();
                    ctx.fill();
                }
            }
        }

        // 动画循环
        function animate() {
            updatePhysics();
            render();
            requestAnimationFrame(animate);
        }

        // 滑块事件
        document.getElementById('windSlider').addEventListener('input', (e) => {
            state.windSpeed = parseFloat(e.target.value);
            document.getElementById('windValue').textContent = state.windSpeed + ' m/s';
        });

        document.getElementById('humiditySlider').addEventListener('input', (e) => {
            state.humidity = parseFloat(e.target.value);
            document.getElementById('humidityValue').textContent = state.humidity + '%';
        });

        // 启动
        initWater();
        animate();
    </script>
</body>
</html>$HTML$,
 75,
 74,
 873,
 false,
 0,
 NOW(),
 '{"name": "水循环", "description": "地球水循环过程：蒸发、降水、径流的动态展示", "difficulty": "medium", "render_mode": "html"}');


-- [23/24] 气候带分布 (geography, 75分)
INSERT INTO simulator_templates
(subject, topic, code, quality_score, visual_elements, line_count, has_setup_update, variable_count, created_at, metadata)
VALUES
('geography',
 '气候带分布',
 $HTML$<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>气候带模拟器 - 地理学</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%);
            color: #F1F5F9;
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        header {
            text-align: center;
            margin-bottom: 25px;
            padding: 20px;
            background: rgba(59, 130, 246, 0.15);
            border-radius: 12px;
            border: 2px solid rgba(59, 130, 246, 0.3);
        }

        h1 {
            font-size: 2.5em;
            color: #60A5FA;
            margin-bottom: 8px;
        }

        .subtitle {
            font-size: 1.1em;
            color: #CBD5E1;
        }

        .main-layout {
            display: grid;
            grid-template-columns: 1fr 320px;
            gap: 20px;
            margin-bottom: 20px;
        }

        .canvas-wrapper {
            background: rgba(15, 23, 42, 0.7);
            border-radius: 12px;
            padding: 15px;
            border: 2px solid rgba(59, 130, 246, 0.3);
        }

        canvas {
            width: 100%;
            height: 550px;
            border-radius: 8px;
            display: block;
            background: #000;
        }

        .control-panel {
            background: rgba(15, 23, 42, 0.7);
            border-radius: 12px;
            padding: 18px;
            border: 2px solid rgba(59, 130, 246, 0.3);
        }

        .control-section {
            margin-bottom: 22px;
        }

        .control-section h3 {
            color: #60A5FA;
            margin-bottom: 10px;
            font-size: 1em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        button {
            width: 100%;
            padding: 10px;
            margin: 5px 0;
            border: none;
            border-radius: 6px;
            font-size: 0.95em;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 600;
        }

        .btn-season {
            background: #3B82F6;
            color: white;
        }

        .btn-season:hover {
            background: #2563EB;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
        }

        .btn-view {
            background: #10B981;
            color: white;
        }

        .btn-view:hover {
            background: #059669;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
        }

        .btn-control {
            background: #F59E0B;
            color: white;
        }

        .btn-control:hover {
            background: #D97706;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(245, 158, 11, 0.4);
        }

        .slider-group {
            margin: 12px 0;
        }

        .slider-group label {
            display: flex;
            justify-content: space-between;
            margin-bottom: 6px;
            color: #CBD5E1;
            font-size: 0.9em;
        }

        .value-badge {
            background: rgba(59, 130, 246, 0.3);
            padding: 2px 10px;
            border-radius: 4px;
            font-weight: 600;
            color: #60A5FA;
        }

        input[type="range"] {
            width: 100%;
            height: 6px;
            border-radius: 3px;
            background: rgba(148, 163, 184, 0.3);
            outline: none;
            -webkit-appearance: none;
        }

        input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            width: 16px;
            height: 16px;
            border-radius: 50%;
            background: #3B82F6;
            cursor: pointer;
            transition: all 0.3s;
        }

        input[type="range"]::-webkit-slider-thumb:hover {
            background: #60A5FA;
            transform: scale(1.2);
        }

        .legend {
            margin-top: 15px;
        }

        .legend-item {
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 8px 0;
            padding: 8px;
            background: rgba(59, 130, 246, 0.1);
            border-radius: 6px;
        }

        .legend-color {
            width: 28px;
            height: 28px;
            border-radius: 4px;
            border: 2px solid rgba(255, 255, 255, 0.3);
        }

        .legend-text {
            flex: 1;
        }

        .legend-name {
            font-weight: 600;
            color: #F1F5F9;
            font-size: 0.9em;
        }

        .legend-range {
            font-size: 0.75em;
            color: #94A3B8;
        }

        .info-panel {
            background: rgba(15, 23, 42, 0.7);
            border-radius: 12px;
            padding: 20px;
            border: 2px solid rgba(59, 130, 246, 0.3);
        }

        .info-panel h3 {
            color: #60A5FA;
            margin-bottom: 15px;
            font-size: 1.2em;
        }

        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 12px;
        }

        .info-card {
            background: rgba(59, 130, 246, 0.15);
            padding: 12px;
            border-radius: 8px;
            border: 1px solid rgba(59, 130, 246, 0.3);
        }

        .info-card h4 {
            color: #10B981;
            font-size: 0.85em;
            margin-bottom: 6px;
            text-transform: uppercase;
        }

        .info-card p {
            font-size: 1.3em;
            font-weight: 600;
            color: #F1F5F9;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🌍 气候带模拟器</h1>
            <p class="subtitle">探索地球气候带分布与季节变化</p>
        </header>

        <div class="main-layout">
            <div class="canvas-wrapper">
                <canvas id="canvas"></canvas>
            </div>

            <div class="control-panel">
                <div class="control-section">
                    <h3>季节选择</h3>
                    <button class="btn-season" onclick="changeSeason('spring')">🌱 春分 (3月)</button>
                    <button class="btn-season" onclick="changeSeason('summer')">☀️ 夏至 (6月)</button>
                    <button class="btn-season" onclick="changeSeason('autumn')">🍂 秋分 (9月)</button>
                    <button class="btn-season" onclick="changeSeason('winter')">❄️ 冬至 (12月)</button>
                </div>

                <div class="control-section">
                    <h3>视角切换</h3>
                    <button class="btn-view" onclick="changeView('globe')">🌐 球体视角</button>
                    <button class="btn-view" onclick="changeView('section')">📊 剖面图</button>
                </div>

                <div class="control-section">
                    <h3>动画控制</h3>
                    <button class="btn-control" onclick="toggleAnimation()">▶️ 开始/暂停</button>
                    <button class="btn-control" onclick="toggleRotation()">🔄 旋转地球</button>
                </div>

                <div class="control-section">
                    <h3>参数调节</h3>
                    <div class="slider-group">
                        <label>
                            <span>地轴倾角</span>
                            <span class="value-badge" id="tiltDisplay">23.5°</span>
                        </label>
                        <input type="range" id="tiltSlider" min="0" max="45" step="0.5" value="23.5">
                    </div>
                    <div class="slider-group">
                        <label>
                            <span>动画速度</span>
                            <span class="value-badge" id="speedDisplay">1.0x</span>
                        </label>
                        <input type="range" id="speedSlider" min="0.1" max="3" step="0.1" value="1">
                    </div>
                </div>

                <div class="legend">
                    <div class="legend-item">
                        <div class="legend-color" style="background: #EF4444;"></div>
                        <div class="legend-text">
                            <div class="legend-name">热带</div>
                            <div class="legend-range">23.5°S ~ 23.5°N</div>
                        </div>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #F59E0B;"></div>
                        <div class="legend-text">
                            <div class="legend-name">北温带</div>
                            <div class="legend-range">23.5°N ~ 66.5°N</div>
                        </div>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #10B981;"></div>
                        <div class="legend-text">
                            <div class="legend-name">南温带</div>
                            <div class="legend-range">23.5°S ~ 66.5°S</div>
                        </div>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #3B82F6;"></div>
                        <div class="legend-text">
                            <div class="legend-name">北寒带</div>
                            <div class="legend-range">66.5°N ~ 90°N</div>
                        </div>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #06B6D4;"></div>
                        <div class="legend-text">
                            <div class="legend-name">南寒带</div>
                            <div class="legend-range">66.5°S ~ 90°S</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="info-panel">
            <h3>📊 实时气候数据</h3>
            <div class="info-grid">
                <div class="info-card">
                    <h4>当前季节</h4>
                    <p id="seasonInfo">春分</p>
                </div>
                <div class="info-card">
                    <h4>太阳直射点</h4>
                    <p id="directInfo">0°</p>
                </div>
                <div class="info-card">
                    <h4>北半球温度</h4>
                    <p id="northTemp">18°C</p>
                </div>
                <div class="info-card">
                    <h4>南半球温度</h4>
                    <p id="southTemp">18°C</p>
                </div>
                <div class="info-card">
                    <h4>赤道温度</h4>
                    <p id="equatorTemp">28°C</p>
                </div>
                <div class="info-card">
                    <h4>极地温度</h4>
                    <p id="polarTemp">-25°C</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');

        // 设置canvas分辨率
        function setupCanvas() {
            const rect = canvas.getBoundingClientRect();
            canvas.width = rect.width * window.devicePixelRatio;
            canvas.height = rect.height * window.devicePixelRatio;
            ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
        }
        setupCanvas();
        window.addEventListener('resize', setupCanvas);

        // 全局状态
        const state = {
            view: 'globe',
            season: 'spring',
            axialTilt: 23.5,
            speed: 1.0,
            time: 0,
            rotation: 0,
            animating: false,
            rotating: false
        };

        // 生成固定位置的星星
        const stars = [];
        function initStars() {
            const w = canvas.getBoundingClientRect().width;
            const h = canvas.getBoundingClientRect().height;
            stars.length = 0;
            for (let i = 0; i < 100; i++) {
                stars.push({
                    x: Math.random() * w,
                    y: Math.random() * h,
                    baseBrightness: 0.3 + Math.random() * 0.7,
                    size: 0.5 + Math.random() * 1.5,
                    phase: Math.random() * Math.PI * 2,
                    speed: 0.5 + Math.random() * 1.5
                });
            }
        }
        initStars();
        window.addEventListener('resize', initStars);

        // 气候带定义
        const zones = [
            { name: '北寒带', minLat: 66.5, maxLat: 90, color: '#3B82F6' },
            { name: '北温带', minLat: 23.5, maxLat: 66.5, color: '#F59E0B' },
            { name: '热带', minLat: -23.5, maxLat: 23.5, color: '#EF4444' },
            { name: '南温带', minLat: -66.5, maxLat: -23.5, color: '#10B981' },
            { name: '南寒带', minLat: -90, maxLat: -66.5, color: '#06B6D4' }
        ];

        function getZoneColor(lat) {
            for (let z of zones) {
                if (lat >= z.minLat && lat <= z.maxLat) return z.color;
            }
            return '#666';
        }

        // 季节映射
        const seasons = {
            spring: { angle: 0, name: '春分', directLat: 0 },
            summer: { angle: Math.PI / 2, name: '夏至', directLat: 23.5 },
            autumn: { angle: Math.PI, name: '秋分', directLat: 0 },
            winter: { angle: Math.PI * 1.5, name: '冬至', directLat: -23.5 }
        };

        function changeSeason(season) {
            state.season = season;
            state.time = seasons[season].angle;
            updateInfo();
        }

        function changeView(view) {
            state.view = view;
        }

        function toggleAnimation() {
            state.animating = !state.animating;
        }

        function toggleRotation() {
            state.rotating = !state.rotating;
        }

        // 更新信息面板
        function updateInfo() {
            const s = seasons[state.season];
            const directLat = Math.sin(state.time) * state.axialTilt;

            document.getElementById('seasonInfo').textContent = s.name;
            document.getElementById('directInfo').textContent = Math.round(directLat * 10) / 10 + '°';

            const northTemp = 18 + directLat * 0.8;
            const southTemp = 18 - directLat * 0.8;
            const equatorTemp = 28 - Math.abs(directLat) * 0.15;
            const polarTemp = -25 - Math.abs(directLat) * 0.2;

            document.getElementById('northTemp').textContent = Math.round(northTemp) + '°C';
            document.getElementById('southTemp').textContent = Math.round(southTemp) + '°C';
            document.getElementById('equatorTemp').textContent = Math.round(equatorTemp) + '°C';
            document.getElementById('polarTemp').textContent = Math.round(polarTemp) + '°C';
        }

        // 渲染球体视角
        function renderGlobe() {
            const w = canvas.getBoundingClientRect().width;
            const h = canvas.getBoundingClientRect().height;
            const cx = w / 2;
            const cy = h / 2;
            const r = Math.min(w, h) * 0.32;

            // 背景
            ctx.fillStyle = '#000';
            ctx.fillRect(0, 0, w, h);

            // 星星（缓慢闪烁）
            const time = Date.now() / 1000;
            stars.forEach(star => {
                const twinkle = Math.sin(time * star.speed + star.phase) * 0.3;
                const brightness = Math.max(0.2, Math.min(1, star.baseBrightness + twinkle));
                ctx.fillStyle = `rgba(255, 255, 255, ${brightness})`;
                ctx.beginPath();
                ctx.arc(star.x, star.y, star.size, 0, Math.PI * 2);
                ctx.fill();
            });

            // 太阳位置
            const sunAngle = state.time;
            const sunDist = r * 2.8;
            const sunX = cx + Math.cos(sunAngle) * sunDist;
            const sunY = cy + Math.sin(sunAngle) * sunDist * 0.6;

            // 太阳光晕
            const sunGrad = ctx.createRadialGradient(sunX, sunY, 0, sunX, sunY, 55);
            sunGrad.addColorStop(0, '#FFF');
            sunGrad.addColorStop(0.3, '#FBBF24');
            sunGrad.addColorStop(1, 'rgba(251, 191, 36, 0)');
            ctx.fillStyle = sunGrad;
            ctx.beginPath();
            ctx.arc(sunX, sunY, 55, 0, Math.PI * 2);
            ctx.fill();

            // 太阳核心
            ctx.fillStyle = '#FEF3C7';
            ctx.beginPath();
            ctx.arc(sunX, sunY, 25, 0, Math.PI * 2);
            ctx.fill();

            ctx.save();
            ctx.translate(cx, cy);
            ctx.rotate(state.axialTilt * Math.PI / 180);

            // 绘制地球气候带
            const bands = 60;
            for (let i = 0; i < bands; i++) {
                const lat1 = 90 - (i / bands) * 180;
                const lat2 = 90 - ((i + 1) / bands) * 180;
                const avgLat = (lat1 + lat2) / 2;

                const y1 = -Math.sin(lat1 * Math.PI / 180) * r;
                const y2 = -Math.sin(lat2 * Math.PI / 180) * r;
                const rx = Math.cos(avgLat * Math.PI / 180) * r * Math.abs(Math.cos(state.rotation));

                const color = getZoneColor(avgLat);

                // 光照计算
                const lightDir = sunAngle + Math.PI;
                const bandAngle = Math.atan2((y1 + y2) / 2, rx);
                const lightness = Math.max(0.3, Math.cos(bandAngle - lightDir) * 0.5 + 0.5);

                ctx.fillStyle = color;
                ctx.globalAlpha = lightness;
                ctx.beginPath();
                ctx.ellipse(0, (y1 + y2) / 2, Math.abs(rx), Math.abs(y2 - y1) / 2, 0, 0, Math.PI * 2);
                ctx.fill();
            }
            ctx.globalAlpha = 1;

            // 纬度线
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.25)';
            ctx.lineWidth = 1;
            [66.5, 23.5, 0, -23.5, -66.5].forEach(lat => {
                const y = -Math.sin(lat * Math.PI / 180) * r;
                const rx = Math.cos(lat * Math.PI / 180) * r;
                ctx.beginPath();
                ctx.ellipse(0, y, rx * Math.abs(Math.cos(state.rotation)), rx * Math.abs(Math.sin(state.rotation)), 0, 0, Math.PI * 2);
                ctx.stroke();
            });

            // 地轴
            ctx.strokeStyle = '#F59E0B';
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.moveTo(0, -r * 1.3);
            ctx.lineTo(0, r * 1.3);
            ctx.stroke();

            // 标记N/S
            ctx.fillStyle = '#FFF';
            ctx.font = 'bold 14px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText('N', 0, -r * 1.38);
            ctx.fillText('S', 0, r * 1.42);

            ctx.restore();

            // 太阳光线
            const directLat = Math.sin(state.time) * state.axialTilt;
            const directY = cy - Math.sin(directLat * Math.PI / 180) * r * Math.cos(state.axialTilt * Math.PI / 180);

            ctx.strokeStyle = 'rgba(251, 191, 36, 0.4)';
            ctx.lineWidth = 2;
            for (let i = -3; i <= 3; i++) {
                ctx.beginPath();
                ctx.moveTo(sunX, sunY);
                ctx.lineTo(cx - r * 0.9, directY + i * 20);
                ctx.stroke();
            }

            // 直射点标记
            ctx.fillStyle = '#FBBF24';
            ctx.beginPath();
            ctx.arc(cx, directY, 7, 0, Math.PI * 2);
            ctx.fill();
            ctx.strokeStyle = '#FEF3C7';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.arc(cx, directY, 13, 0, Math.PI * 2);
            ctx.stroke();
        }

        // 渲染剖面图
        function renderSection() {
            const w = canvas.getBoundingClientRect().width;
            const h = canvas.getBoundingClientRect().height;
            const cx = w / 2;
            const cy = h / 2;
            const r = Math.min(w, h) * 0.32;

            // 背景
            ctx.fillStyle = '#000';
            ctx.fillRect(0, 0, w, h);

            // 太阳
            const sunAngle = state.time;
            const sunX = cx + Math.cos(sunAngle) * r * 2.5;
            const sunY = cy + Math.sin(sunAngle) * r * 1.5;

            const sunGrad = ctx.createRadialGradient(sunX, sunY, 0, sunX, sunY, 45);
            sunGrad.addColorStop(0, '#FFF');
            sunGrad.addColorStop(0.4, '#FBBF24');
            sunGrad.addColorStop(1, '#F59E0B');
            ctx.fillStyle = sunGrad;
            ctx.beginPath();
            ctx.arc(sunX, sunY, 45, 0, Math.PI * 2);
            ctx.fill();

            ctx.save();
            ctx.translate(cx, cy);
            ctx.rotate(state.axialTilt * Math.PI / 180);

            // 绘制气候带剖面
            const zoneData = [
                { lat: 90, next: 66.5, color: '#3B82F6', label: '北寒带' },
                { lat: 66.5, next: 23.5, color: '#F59E0B', label: '北温带' },
                { lat: 23.5, next: -23.5, color: '#EF4444', label: '热带' },
                { lat: -23.5, next: -66.5, color: '#10B981', label: '南温带' },
                { lat: -66.5, next: -90, color: '#06B6D4', label: '南寒带' }
            ];

            zoneData.forEach(zone => {
                const y1 = -Math.sin(zone.lat * Math.PI / 180) * r;
                const y2 = -Math.sin(zone.next * Math.PI / 180) * r;
                const angle1 = Math.asin(-y1 / r);
                const angle2 = Math.asin(-y2 / r);

                ctx.fillStyle = zone.color;
                ctx.beginPath();
                ctx.arc(0, 0, r, angle1, angle2);
                ctx.lineTo(0, y2);
                ctx.lineTo(0, y1);
                ctx.closePath();
                ctx.fill();

                // 标签
                const labelY = (y1 + y2) / 2;
                const labelX = Math.sqrt(r * r - labelY * labelY) + 15;
                ctx.fillStyle = '#FFF';
                ctx.font = 'bold 13px sans-serif';
                ctx.textAlign = 'left';
                ctx.fillText(zone.label, labelX, labelY + 5);
            });

            // 地球轮廓
            ctx.strokeStyle = '#FFF';
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.arc(0, 0, r, 0, Math.PI * 2);
            ctx.stroke();

            // 纬度线
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
            ctx.lineWidth = 1.5;
            ctx.setLineDash([5, 5]);
            [66.5, 23.5, 0, -23.5, -66.5].forEach(lat => {
                const y = -Math.sin(lat * Math.PI / 180) * r;
                ctx.beginPath();
                ctx.moveTo(-r, y);
                ctx.lineTo(r, y);
                ctx.stroke();
            });
            ctx.setLineDash([]);

            // 地轴
            ctx.strokeStyle = '#F59E0B';
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.moveTo(0, -r * 1.3);
            ctx.lineTo(0, r * 1.3);
            ctx.stroke();

            ctx.restore();

            // 太阳光线到直射点
            const directLat = Math.sin(state.time) * state.axialTilt;
            const directY = cy - Math.sin(directLat * Math.PI / 180) * r * Math.cos(state.axialTilt * Math.PI / 180);

            ctx.strokeStyle = 'rgba(251, 191, 36, 0.5)';
            ctx.lineWidth = 2.5;
            for (let i = -2; i <= 2; i++) {
                ctx.beginPath();
                ctx.moveTo(sunX, sunY);
                ctx.lineTo(cx - r * 1.15, directY + i * 25);
                ctx.stroke();
            }

            // 直射点
            ctx.fillStyle = '#FBBF24';
            ctx.beginPath();
            ctx.arc(cx, directY, 8, 0, Math.PI * 2);
            ctx.fill();

            ctx.fillStyle = '#FFF';
            ctx.font = 'bold 12px sans-serif';
            ctx.textAlign = 'right';
            ctx.fillText('直射点', cx - 20, directY + 4);
        }

        // 更新物理
        function updatePhysics() {
            if (state.animating) {
                state.time += 0.008 * state.speed;
                if (state.time > Math.PI * 2) state.time -= Math.PI * 2;
                updateInfo();
            }
            if (state.rotating) {
                state.rotation += 0.01 * state.speed;
            }
        }

        // 渲染
        function render() {
            if (state.view === 'globe') {
                renderGlobe();
            } else {
                renderSection();
            }
        }

        // 动画循环
        function animate() {
            updatePhysics();
            render();
            requestAnimationFrame(animate);
        }

        // 滑块事件
        document.getElementById('tiltSlider').addEventListener('input', (e) => {
            state.axialTilt = parseFloat(e.target.value);
            document.getElementById('tiltDisplay').textContent = state.axialTilt.toFixed(1) + '°';
        });

        document.getElementById('speedSlider').addEventListener('input', (e) => {
            state.speed = parseFloat(e.target.value);
            document.getElementById('speedDisplay').textContent = state.speed.toFixed(1) + 'x';
        });

        // 启动
        updateInfo();
        animate();
    </script>
</body>
</html>
$HTML$,
 75,
 112,
 771,
 false,
 0,
 NOW(),
 '{"name": "气候带分布", "description": "全球气候带的分布和特征，受纬度和地形影响", "difficulty": "medium", "render_mode": "html"}');


-- [24/24] 板块运动 (geography, 75分)
INSERT INTO simulator_templates
(subject, topic, code, quality_score, visual_elements, line_count, has_setup_update, variable_count, created_at, metadata)
VALUES
('geography',
 '板块运动',
 $HTML$<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>板块构造模拟器 - 地理学</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
            color: #F1F5F9;
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(14, 165, 233, 0.1);
            border-radius: 12px;
            border: 1px solid rgba(14, 165, 233, 0.3);
        }

        h1 {
            font-size: 2.5em;
            color: #0EA5E9;
            margin-bottom: 10px;
        }

        .subtitle {
            font-size: 1.1em;
            color: #94A3B8;
        }

        .main-content {
            display: grid;
            grid-template-columns: 1fr 350px;
            gap: 20px;
            margin-bottom: 20px;
        }

        .canvas-container {
            background: rgba(15, 23, 42, 0.6);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(14, 165, 233, 0.3);
        }

        canvas {
            width: 100%;
            height: 600px;
            border-radius: 8px;
            background: #0F172A;
            display: block;
        }

        .controls-panel {
            background: rgba(15, 23, 42, 0.6);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(14, 165, 233, 0.3);
        }

        .control-group {
            margin-bottom: 25px;
        }

        .control-group h3 {
            color: #0EA5E9;
            margin-bottom: 12px;
            font-size: 1.1em;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .control-group h3::before {
            content: '▶';
            font-size: 0.8em;
        }

        button {
            width: 100%;
            padding: 12px;
            margin: 6px 0;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 500;
        }

        .btn-primary {
            background: #0EA5E9;
            color: white;
        }

        .btn-primary:hover {
            background: #0284C7;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(14, 165, 233, 0.4);
        }

        .btn-secondary {
            background: #10B981;
            color: white;
        }

        .btn-secondary:hover {
            background: #059669;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
        }

        .btn-accent {
            background: #F59E0B;
            color: white;
        }

        .btn-accent:hover {
            background: #D97706;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(245, 158, 11, 0.4);
        }

        .slider-control {
            margin: 15px 0;
        }

        .slider-control label {
            display: block;
            margin-bottom: 8px;
            color: #94A3B8;
            font-size: 0.9em;
        }

        input[type="range"] {
            width: 100%;
            height: 6px;
            border-radius: 3px;
            background: rgba(148, 163, 184, 0.2);
            outline: none;
            -webkit-appearance: none;
        }

        input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: #0EA5E9;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        input[type="range"]::-webkit-slider-thumb:hover {
            background: #0284C7;
            transform: scale(1.2);
        }

        .value-display {
            display: inline-block;
            background: rgba(14, 165, 233, 0.2);
            padding: 4px 12px;
            border-radius: 6px;
            font-weight: 600;
            color: #0EA5E9;
            float: right;
        }

        .info-panel {
            background: rgba(15, 23, 42, 0.6);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(14, 165, 233, 0.3);
        }

        .info-panel h3 {
            color: #0EA5E9;
            margin-bottom: 15px;
            font-size: 1.2em;
        }

        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }

        .info-card {
            background: rgba(14, 165, 233, 0.1);
            padding: 15px;
            border-radius: 8px;
            border: 1px solid rgba(14, 165, 233, 0.2);
        }

        .info-card h4 {
            color: #10B981;
            font-size: 0.9em;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .info-card p {
            font-size: 1.4em;
            font-weight: 600;
            color: #F1F5F9;
        }

        .legend {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-top: 15px;
        }

        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .legend-color {
            width: 24px;
            height: 24px;
            border-radius: 4px;
            border: 2px solid rgba(241, 245, 249, 0.3);
        }

        .legend-label {
            font-size: 0.9em;
            color: #CBD5E1;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }

        .active-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #10B981;
            margin-left: 8px;
            animation: pulse 2s ease-in-out infinite;
        }

        @media (max-width: 1024px) {
            .main-content {
                grid-template-columns: 1fr;
            }

            .info-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🌍 板块构造模拟器</h1>
            <p class="subtitle">探索地球板块运动与地质现象的形成机制</p>
        </header>

        <div class="main-content">
            <div class="canvas-container">
                <canvas id="simulatorCanvas"></canvas>
            </div>

            <div class="controls-panel">
                <div class="control-group">
                    <h3>板块运动类型</h3>
                    <button class="btn-primary" onclick="setPlateMode('divergent')">离散边界 ⬅️ ➡️</button>
                    <button class="btn-secondary" onclick="setPlateMode('convergent')">聚合边界 ➡️ ⬅️</button>
                    <button class="btn-accent" onclick="setPlateMode('transform')">转换边界 ⬆️ ⬇️</button>
                </div>

                <div class="control-group">
                    <h3>地质活动</h3>
                    <button class="btn-primary" onclick="triggerEarthquake()">⚡ 触发地震</button>
                    <button class="btn-accent" onclick="triggerVolcano()">🌋 火山喷发</button>
                </div>

                <div class="control-group">
                    <h3>模拟控制</h3>
                    <button class="btn-secondary" onclick="toggleSimulation()">▶️ 开始/暂停</button>
                    <button class="btn-primary" onclick="resetSimulation()">🔄 重置</button>
                </div>

                <div class="control-group">
                    <h3>参数调节</h3>
                    <div class="slider-control">
                        <label>
                            运动速度
                            <span class="value-display" id="speedValue">1.0x</span>
                        </label>
                        <input type="range" id="speedSlider" min="0.1" max="3" step="0.1" value="1">
                    </div>
                    <div class="slider-control">
                        <label>
                            地震强度
                            <span class="value-display" id="magnitudeValue">6.0</span>
                        </label>
                        <input type="range" id="magnitudeSlider" min="3" max="9" step="0.1" value="6">
                    </div>
                </div>

                <div class="legend">
                    <div class="legend-item">
                        <div class="legend-color" style="background: #EF4444;"></div>
                        <span class="legend-label">大陆板块</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #3B82F6;"></div>
                        <span class="legend-label">海洋板块</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: #F59E0B;"></div>
                        <span class="legend-label">岩浆</span>
                    </div>
                </div>
            </div>
        </div>

        <div class="info-panel">
            <h3>地质活动统计 <span class="active-indicator"></span></h3>
            <div class="info-grid">
                <div class="info-card">
                    <h4>板块运动模式</h4>
                    <p id="plateMode">离散边界</p>
                </div>
                <div class="info-card">
                    <h4>地震次数</h4>
                    <p id="earthquakeCount">0</p>
                </div>
                <div class="info-card">
                    <h4>火山喷发</h4>
                    <p id="volcanoCount">0</p>
                </div>
                <div class="info-card">
                    <h4>模拟时间</h4>
                    <p id="simTime">0 年</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('simulatorCanvas');
        const ctx = canvas.getContext('2d');

        // 设置canvas实际分辨率
        function resizeCanvas() {
            const rect = canvas.getBoundingClientRect();
            canvas.width = rect.width * window.devicePixelRatio;
            canvas.height = rect.height * window.devicePixelRatio;
            ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
        }
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);

        // 模拟状态
        let state = {
            running: false,
            mode: 'divergent',
            speed: 1.0,
            magnitude: 6.0,
            time: 0,
            earthquakeCount: 0,
            volcanoCount: 0,
            plates: [],
            earthquakes: [],
            volcanoes: [],
            magma: [],
            stress: 0, // 应力积累
            shakeOffset: { x: 0, y: 0 } // 地震震动偏移
        };

        // 初始化板块
        function initPlates() {
            const w = canvas.getBoundingClientRect().width;
            const h = canvas.getBoundingClientRect().height;

            state.plates = [
                {
                    x: 0,
                    y: h * 0.3,
                    width: w * 0.45,
                    height: h * 0.4,
                    vx: 0,
                    vy: 0,
                    angle: 0, // 板块倾斜角度
                    offset: 0,
                    color: '#EF4444',
                    type: 'continental',
                    label: '大陆板块'
                },
                {
                    x: w * 0.55,
                    y: h * 0.3,
                    width: w * 0.45,
                    height: h * 0.4,
                    vx: 0,
                    vy: 0,
                    angle: 0,
                    offset: 0,
                    color: '#3B82F6',
                    type: 'oceanic',
                    label: '海洋板块'
                }
            ];
        }

        // 设置板块运动模式
        function setPlateMode(mode) {
            state.mode = mode;
            const w = canvas.getBoundingClientRect().width;

            // 重置板块位置和角度
            state.plates[0].x = 0;
            state.plates[0].width = w * 0.45;
            state.plates[0].angle = 0;
            state.plates[0].offset = 0;
            state.plates[1].x = w * 0.55;
            state.plates[1].width = w * 0.45;
            state.plates[1].angle = 0;
            state.plates[1].offset = 0;

            switch(mode) {
                case 'divergent':
                    // 离散边界：板块相互远离，中间岩浆上涌
                    state.plates[0].vx = -0.5;
                    state.plates[0].vy = 0;
                    state.plates[1].vx = 0.5;
                    state.plates[1].vy = 0;
                    document.getElementById('plateMode').textContent = '离散边界';
                    break;
                case 'convergent':
                    // 聚合边界：海洋板块俯冲到大陆板块下方
                    state.plates[0].vx = 0.3; // 大陆板块缓慢移动
                    state.plates[0].vy = 0;
                    state.plates[1].vx = -0.8; // 海洋板块快速俯冲
                    state.plates[1].vy = 0;
                    document.getElementById('plateMode').textContent = '聚合边界';
                    break;
                case 'transform':
                    // 转换边界：板块沿断层水平错动
                    state.plates[0].vx = 0;
                    state.plates[0].vy = -0.5;
                    state.plates[1].vx = 0;
                    state.plates[1].vy = 0.5;
                    document.getElementById('plateMode').textContent = '转换边界';
                    break;
            }
        }

        // 触发地震
        function triggerEarthquake() {
            const w = canvas.getBoundingClientRect().width;
            const h = canvas.getBoundingClientRect().height;
            const mag = state.magnitude;

            // 根据板块边界模式确定地震位置
            let earthquakeX, earthquakeY;
            if(state.mode === 'convergent' && state.plates.length >= 2) {
                // 聚合边界：俯冲带地震
                earthquakeX = state.plates[0].x + state.plates[0].width;
                earthquakeY = h * 0.5;
            } else if(state.mode === 'transform' && state.plates.length >= 2) {
                // 转换边界：断层地震
                earthquakeX = w * 0.5;
                earthquakeY = h * 0.5;
            } else {
                // 离散边界或默认位置
                earthquakeX = w * 0.5;
                earthquakeY = h * 0.5;
            }

            createEarthquake(earthquakeX, earthquakeY, mag);
        }

        // 创建地震（内部函数）
        function createEarthquake(x, y, magnitude) {
            const earthquake = {
                x: x,
                y: y,
                magnitude: magnitude,
                waves: [
                    { radius: 0, alpha: 1, speed: 5 }  // P波（快速）
                ],
                shakeIntensity: magnitude * 2,
                shakeDuration: magnitude * 10
            };

            state.earthquakes.push(earthquake);

            // 添加S波（较慢但更强）
            setTimeout(() => {
                if(earthquake.waves) {
                    earthquake.waves.push({ radius: 0, alpha: 1, speed: 3 });
                }
            }, 300);

            // 添加面波（最慢但破坏力大）
            setTimeout(() => {
                if(earthquake.waves) {
                    earthquake.waves.push({ radius: 0, alpha: 1.2, speed: 2 });
                }
            }, 600);

            state.earthquakeCount++;
            document.getElementById('earthquakeCount').textContent = state.earthquakeCount;

            // 地震引起震动
            startShaking(earthquake.shakeIntensity, earthquake.shakeDuration);

            // 聚合边界的强震可能触发火山
            if(state.mode === 'convergent' && magnitude >= 6.5 && Math.random() < 0.5) {
                setTimeout(() => {
                    triggerVolcano();
                }, 1000);
            }

            // 释放应力
            state.stress = Math.max(0, state.stress - magnitude * 10);
        }

        // 开始震动效果
        function startShaking(intensity, duration) {
            const startTime = Date.now();
            const shake = () => {
                const elapsed = Date.now() - startTime;
                if(elapsed < duration) {
                    const decay = 1 - (elapsed / duration);
                    state.shakeOffset.x = (Math.random() - 0.5) * intensity * decay;
                    state.shakeOffset.y = (Math.random() - 0.5) * intensity * decay;
                    requestAnimationFrame(shake);
                } else {
                    state.shakeOffset.x = 0;
                    state.shakeOffset.y = 0;
                }
            };
            shake();
        }

        // 触发火山
        function triggerVolcano() {
            const w = canvas.getBoundingClientRect().width;
            const h = canvas.getBoundingClientRect().height;

            state.volcanoes.push({
                x: w * 0.5 + (Math.random() - 0.5) * 100,
                y: h * 0.7,
                particles: [],
                life: 0
            });

            state.volcanoCount++;
            document.getElementById('volcanoCount').textContent = state.volcanoCount;
        }

        // 切换模拟
        function toggleSimulation() {
            state.running = !state.running;
            if(state.running && state.plates.length === 0) {
                initPlates();
            }
        }

        // 重置模拟
        function resetSimulation() {
            state = {
                running: false,
                mode: 'divergent',
                speed: 1.0,
                magnitude: 6.0,
                time: 0,
                earthquakeCount: 0,
                volcanoCount: 0,
                plates: [],
                earthquakes: [],
                volcanoes: [],
                magma: [],
                stress: 0,
                shakeOffset: { x: 0, y: 0 }
            };
            document.getElementById('earthquakeCount').textContent = '0';
            document.getElementById('volcanoCount').textContent = '0';
            document.getElementById('simTime').textContent = '0 年';
            document.getElementById('plateMode').textContent = '离散边界';
            document.getElementById('speedSlider').value = '1';
            document.getElementById('speedValue').textContent = '1.0x';
            document.getElementById('magnitudeSlider').value = '6';
            document.getElementById('magnitudeValue').textContent = '6.0';
            initPlates();
        }

        // 更新物理
        function updatePhysics() {
            if(!state.running) return;

            const w = canvas.getBoundingClientRect().width;
            const h = canvas.getBoundingClientRect().height;

            state.time += state.speed * 0.1;
            document.getElementById('simTime').textContent = Math.floor(state.time) + ' 年';

            // 更新板块位置
            if(state.mode === 'divergent') {
                // 离散边界：板块分离，中间产生裂谷和岩浆
                state.plates[0].x += state.plates[0].vx * state.speed;
                state.plates[1].x += state.plates[1].vx * state.speed;

                // 限制分离距离
                const gap = state.plates[1].x - (state.plates[0].x + state.plates[0].width);
                if(gap > w * 0.3) {
                    state.plates[0].vx = 0;
                    state.plates[1].vx = 0;
                }

                // 应力缓慢积累
                state.stress += 0.05 * state.speed;

                // 在裂谷中生成岩浆
                if(Math.random() < 0.1) {
                    const gapCenter = state.plates[0].x + state.plates[0].width + gap / 2;
                    state.magma.push({
                        x: gapCenter + (Math.random() - 0.5) * gap,
                        y: h * 0.7,
                        vy: -1 - Math.random() * 2,
                        radius: 3 + Math.random() * 5,
                        alpha: 1
                    });
                }

            } else if(state.mode === 'convergent') {
                // 聚合边界：海洋板块俯冲到大陆板块下方
                const continental = state.plates[0]; // 大陆板块
                const oceanic = state.plates[1];     // 海洋板块

                oceanic.x += oceanic.vx * state.speed;
                continental.x += continental.vx * state.speed;

                // 检测碰撞
                const continentalRight = continental.x + continental.width;
                const collision = oceanic.x <= continentalRight;

                if(collision) {
                    // 应力快速积累
                    state.stress += 0.3 * state.speed;

                    // 海洋板块开始俯冲
                    oceanic.angle = Math.min(oceanic.angle + 0.5, 30); // 俯冲角度
                    oceanic.offset = Math.min(oceanic.offset + 1, 80); // 下沉深度

                    // 大陆板块抬升形成山脉
                    continental.offset = Math.max(continental.offset - 0.3, -30);

                    // 应力达到阈值时自动触发地震
                    if(state.stress >= 100) {
                        const magnitude = 5 + Math.random() * 3; // 5-8级地震
                        createEarthquake(continentalRight, h * 0.5, magnitude);
                    }

                    // 俯冲带产生岩浆
                    if(Math.random() < 0.05) {
                        state.magma.push({
                            x: continentalRight + (Math.random() - 0.5) * 80,
                            y: h * 0.7,
                            vy: -2 - Math.random() * 2,
                            radius: 4 + Math.random() * 6,
                            alpha: 1
                        });
                    }
                }

            } else if(state.mode === 'transform') {
                // 转换边界：板块水平错动
                state.plates[0].y += state.plates[0].vy * state.speed;
                state.plates[1].y += state.plates[1].vy * state.speed;

                // 应力积累
                state.stress += 0.2 * state.speed;

                // 限制移动范围
                if(Math.abs(state.plates[0].y - h * 0.3) > h * 0.15) {
                    state.plates[0].vy = 0;
                }
                if(Math.abs(state.plates[1].y - h * 0.3) > h * 0.15) {
                    state.plates[1].vy = 0;
                }

                // 应力达到阈值时自动触发地震
                if(state.stress >= 80) {
                    const magnitude = 5.5 + Math.random() * 2.5; // 5.5-8级地震
                    createEarthquake(w * 0.5, h * 0.5, magnitude);
                }
            }

            // 更新岩浆
            state.magma = state.magma.filter(m => {
                m.y += m.vy;
                m.alpha -= 0.01;
                return m.alpha > 0 && m.y > h * 0.2;
            });

            // 更新地震波
            state.earthquakes = state.earthquakes.filter(eq => {
                eq.waves.forEach(wave => {
                    wave.radius += wave.speed; // 不同速度的波
                    wave.alpha -= 0.015;
                });
                eq.waves = eq.waves.filter(w => w.alpha > 0 && w.radius < 500);
                return eq.waves.length > 0;
            });

            // 更新火山
            state.volcanoes.forEach(v => {
                v.life++;
                if(v.life < 100 && v.life % 2 === 0) {
                    for(let i = 0; i < 3; i++) {
                        v.particles.push({
                            x: v.x,
                            y: v.y,
                            vx: (Math.random() - 0.5) * 8,
                            vy: -10 - Math.random() * 10,
                            radius: 2 + Math.random() * 4,
                            alpha: 1
                        });
                    }
                }

                v.particles.forEach(p => {
                    p.x += p.vx;
                    p.y += p.vy;
                    p.vy += 0.3; // 重力
                    p.alpha -= 0.015;
                });

                v.particles = v.particles.filter(p => p.alpha > 0);
            });

            state.volcanoes = state.volcanoes.filter(v => v.life < 150);
        }

        // 渲染
        function render() {
            const w = canvas.getBoundingClientRect().width;
            const h = canvas.getBoundingClientRect().height;

            // 清空画布
            ctx.fillStyle = '#0F172A';
            ctx.fillRect(0, 0, w, h);

            // 应用震动效果
            ctx.save();
            ctx.translate(state.shakeOffset.x, state.shakeOffset.y);

            // 绘制地幔层
            const mantleGradient = ctx.createLinearGradient(0, h * 0.7, 0, h);
            mantleGradient.addColorStop(0, '#F59E0B');
            mantleGradient.addColorStop(1, '#DC2626');
            ctx.fillStyle = mantleGradient;
            ctx.fillRect(0, h * 0.7, w, h * 0.3);

            // 绘制岩浆
            state.magma.forEach(m => {
                ctx.globalAlpha = m.alpha;
                const gradient = ctx.createRadialGradient(m.x, m.y, 0, m.x, m.y, m.radius);
                gradient.addColorStop(0, '#FCD34D');
                gradient.addColorStop(1, '#F59E0B');
                ctx.fillStyle = gradient;
                ctx.beginPath();
                ctx.arc(m.x, m.y, m.radius, 0, Math.PI * 2);
                ctx.fill();
            });
            ctx.globalAlpha = 1;

            // 绘制板块
            state.plates.forEach((plate, i) => {
                ctx.save();

                // 根据模式绘制不同形态的板块
                if(state.mode === 'convergent' && plate.type === 'oceanic' && plate.angle > 0) {
                    // 聚合边界：海洋板块俯冲效果
                    ctx.translate(plate.x + plate.width, plate.y);
                    ctx.rotate(plate.angle * Math.PI / 180);
                    ctx.translate(0, plate.offset);

                    // 绘制俯冲的板块（倾斜）
                    ctx.fillStyle = plate.color;
                    ctx.fillRect(-plate.width, 0, plate.width, plate.height);

                    // 板块纹理
                    ctx.strokeStyle = 'rgba(0, 0, 0, 0.3)';
                    ctx.lineWidth = 2;
                    for(let j = 0; j < 5; j++) {
                        ctx.beginPath();
                        ctx.moveTo(-plate.width, plate.height * (j / 5));
                        ctx.lineTo(0, plate.height * (j / 5));
                        ctx.stroke();
                    }

                    // 板块标签
                    ctx.rotate(-plate.angle * Math.PI / 180);
                    ctx.fillStyle = '#F1F5F9';
                    ctx.font = 'bold 16px sans-serif';
                    ctx.textAlign = 'center';
                    ctx.fillText(plate.label, -plate.width / 2, plate.height / 2);

                } else if(state.mode === 'convergent' && plate.type === 'continental' && plate.offset < 0) {
                    // 聚合边界：大陆板块抬升形成山脉
                    ctx.translate(plate.x, plate.y + plate.offset);

                    // 绘制抬升的板块
                    ctx.fillStyle = plate.color;
                    ctx.fillRect(0, 0, plate.width, plate.height);

                    // 山脉轮廓（右侧隆起）
                    ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
                    ctx.beginPath();
                    ctx.moveTo(plate.width - 100, 0);
                    for(let x = 0; x < 100; x += 10) {
                        const y = Math.sin(x / 10) * 20 - Math.abs(plate.offset) * (x / 100);
                        ctx.lineTo(plate.width - 100 + x, y);
                    }
                    ctx.lineTo(plate.width, 0);
                    ctx.closePath();
                    ctx.fill();

                    // 板块纹理
                    ctx.strokeStyle = 'rgba(0, 0, 0, 0.3)';
                    ctx.lineWidth = 2;
                    for(let j = 0; j < 5; j++) {
                        ctx.beginPath();
                        ctx.moveTo(0, plate.height * (j / 5));
                        ctx.lineTo(plate.width, plate.height * (j / 5));
                        ctx.stroke();
                    }

                    // 板块标签
                    ctx.fillStyle = '#F1F5F9';
                    ctx.font = 'bold 16px sans-serif';
                    ctx.textAlign = 'center';
                    ctx.fillText(plate.label, plate.width / 2, plate.height / 2);

                } else {
                    // 正常绘制板块
                    ctx.translate(plate.x, plate.y);

                    ctx.fillStyle = plate.color;
                    ctx.fillRect(0, 0, plate.width, plate.height);

                    // 板块纹理
                    ctx.strokeStyle = 'rgba(0, 0, 0, 0.3)';
                    ctx.lineWidth = 2;
                    for(let j = 0; j < 5; j++) {
                        ctx.beginPath();
                        ctx.moveTo(0, plate.height * (j / 5));
                        ctx.lineTo(plate.width, plate.height * (j / 5));
                        ctx.stroke();
                    }

                    // 板块边界高亮
                    ctx.strokeStyle = 'rgba(255, 255, 255, 0.5)';
                    ctx.lineWidth = 3;
                    ctx.strokeRect(0, 0, plate.width, plate.height);

                    // 板块标签
                    ctx.fillStyle = '#F1F5F9';
                    ctx.font = 'bold 16px sans-serif';
                    ctx.textAlign = 'center';
                    ctx.fillText(plate.label, plate.width / 2, plate.height / 2);
                }

                ctx.restore();
            });

            // 绘制板块边界
            if(state.plates.length >= 2) {
                let boundary;
                if(state.mode === 'divergent') {
                    // 离散边界：裂谷
                    const gap = state.plates[1].x - (state.plates[0].x + state.plates[0].width);
                    const centerX = state.plates[0].x + state.plates[0].width + gap / 2;

                    ctx.strokeStyle = '#F59E0B';
                    ctx.lineWidth = 6;
                    ctx.setLineDash([]);
                    ctx.beginPath();
                    ctx.moveTo(centerX, h * 0.3);
                    ctx.lineTo(centerX, h * 0.7);
                    ctx.stroke();

                    // 裂谷标注
                    ctx.fillStyle = '#FCD34D';
                    ctx.font = 'bold 14px sans-serif';
                    ctx.textAlign = 'center';
                    ctx.fillText('裂谷', centerX, h * 0.25);

                } else if(state.mode === 'convergent') {
                    // 聚合边界：俯冲带
                    boundary = state.plates[0].x + state.plates[0].width;

                    ctx.strokeStyle = '#EF4444';
                    ctx.lineWidth = 4;
                    ctx.setLineDash([10, 5]);
                    ctx.beginPath();
                    ctx.moveTo(boundary, h * 0.2);
                    ctx.lineTo(boundary, h * 0.7);
                    ctx.stroke();
                    ctx.setLineDash([]);

                    // 俯冲带标注
                    ctx.fillStyle = '#FCA5A5';
                    ctx.font = 'bold 14px sans-serif';
                    ctx.textAlign = 'center';
                    ctx.fillText('俯冲带', boundary, h * 0.25);

                } else if(state.mode === 'transform') {
                    // 转换边界：断层
                    boundary = w * 0.5;

                    ctx.strokeStyle = '#8B5CF6';
                    ctx.lineWidth = 4;
                    ctx.setLineDash([15, 10]);
                    ctx.beginPath();
                    ctx.moveTo(boundary, h * 0.2);
                    ctx.lineTo(boundary, h * 0.7);
                    ctx.stroke();
                    ctx.setLineDash([]);

                    // 断层标注
                    ctx.fillStyle = '#C4B5FD';
                    ctx.font = 'bold 14px sans-serif';
                    ctx.textAlign = 'center';
                    ctx.fillText('转换断层', boundary, h * 0.25);
                }
            }

            // 绘制地震波（放在最上层）
            state.earthquakes.forEach(eq => {
                eq.waves.forEach((wave, waveIndex) => {
                    ctx.globalAlpha = wave.alpha * 0.8;

                    // 根据波的类型使用不同颜色
                    let color1, color2, color3;
                    if(waveIndex === 0) {
                        // P波（纵波）- 蓝色系
                        color1 = '#3B82F6';
                        color2 = '#60A5FA';
                        color3 = '#93C5FD';
                    } else if(waveIndex === 1) {
                        // S波（横波）- 红色系
                        color1 = '#EF4444';
                        color2 = '#F87171';
                        color3 = '#FCA5A5';
                    } else {
                        // 面波 - 橙黄色系
                        color1 = '#F59E0B';
                        color2 = '#FBBF24';
                        color3 = '#FCD34D';
                    }

                    // 外层波
                    ctx.strokeStyle = color1;
                    ctx.lineWidth = 5;
                    ctx.beginPath();
                    ctx.arc(eq.x, eq.y, wave.radius, 0, Math.PI * 2);
                    ctx.stroke();

                    // 中层波
                    ctx.strokeStyle = color2;
                    ctx.lineWidth = 3;
                    ctx.beginPath();
                    ctx.arc(eq.x, eq.y, wave.radius + 8, 0, Math.PI * 2);
                    ctx.stroke();

                    // 内层波
                    ctx.strokeStyle = color3;
                    ctx.lineWidth = 2;
                    ctx.beginPath();
                    ctx.arc(eq.x, eq.y, wave.radius + 16, 0, Math.PI * 2);
                    ctx.stroke();
                });

                // 震中标记
                ctx.globalAlpha = 1;
                ctx.fillStyle = '#EF4444';
                ctx.beginPath();
                ctx.arc(eq.x, eq.y, 8, 0, Math.PI * 2);
                ctx.fill();

                ctx.fillStyle = '#FCD34D';
                ctx.beginPath();
                ctx.arc(eq.x, eq.y, 4, 0, Math.PI * 2);
                ctx.fill();

                // 震级标注
                ctx.fillStyle = '#F1F5F9';
                ctx.font = 'bold 14px sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText('M' + eq.magnitude.toFixed(1), eq.x, eq.y - 15);
            });
            ctx.globalAlpha = 1;

            // 恢复震动变换
            ctx.restore();

            // 绘制火山喷发
            state.volcanoes.forEach(v => {
                // 火山锥
                ctx.fillStyle = '#78350F';
                ctx.beginPath();
                ctx.moveTo(v.x, v.y);
                ctx.lineTo(v.x - 30, v.y + 40);
                ctx.lineTo(v.x + 30, v.y + 40);
                ctx.closePath();
                ctx.fill();

                // 喷发粒子
                v.particles.forEach(p => {
                    ctx.globalAlpha = p.alpha;
                    const gradient = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.radius);
                    gradient.addColorStop(0, '#FCD34D');
                    gradient.addColorStop(0.5, '#F59E0B');
                    gradient.addColorStop(1, '#DC2626');
                    ctx.fillStyle = gradient;
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                    ctx.fill();
                });
                ctx.globalAlpha = 1;
            });

            // 绘制运动指示箭头
            if(state.plates.length >= 2) {
                state.plates.forEach((plate, i) => {
                    ctx.fillStyle = '#10B981';
                    ctx.strokeStyle = '#F1F5F9';
                    ctx.lineWidth = 2;

                    const arrowX = plate.x + plate.width / 2;
                    const arrowY = plate.y - 30;
                    const arrowLen = 40;

                    // 箭头方向
                    let dx = plate.vx || 0;
                    let dy = plate.vy || 0;
                    const len = Math.sqrt(dx * dx + dy * dy);
                    if(len > 0) {
                        dx /= len;
                        dy /= len;

                        // 箭头主体
                        ctx.beginPath();
                        ctx.moveTo(arrowX, arrowY);
                        ctx.lineTo(arrowX + dx * arrowLen, arrowY + dy * arrowLen);
                        ctx.stroke();

                        // 箭头头部
                        const angle = Math.atan2(dy, dx);
                        ctx.beginPath();
                        ctx.moveTo(arrowX + dx * arrowLen, arrowY + dy * arrowLen);
                        ctx.lineTo(
                            arrowX + dx * arrowLen - Math.cos(angle - 0.5) * 12,
                            arrowY + dy * arrowLen - Math.sin(angle - 0.5) * 12
                        );
                        ctx.lineTo(
                            arrowX + dx * arrowLen - Math.cos(angle + 0.5) * 12,
                            arrowY + dy * arrowLen - Math.sin(angle + 0.5) * 12
                        );
                        ctx.closePath();
                        ctx.fill();
                    }
                });
            }
        }

        // 动画循环
        function animate() {
            updatePhysics();
            render();
            requestAnimationFrame(animate);
        }

        // 滑块事件
        document.getElementById('speedSlider').addEventListener('input', (e) => {
            state.speed = parseFloat(e.target.value);
            document.getElementById('speedValue').textContent = state.speed.toFixed(1) + 'x';
        });

        document.getElementById('magnitudeSlider').addEventListener('input', (e) => {
            state.magnitude = parseFloat(e.target.value);
            document.getElementById('magnitudeValue').textContent = state.magnitude.toFixed(1);
        });

        // 启动
        initPlates();
        animate();
    </script>
</body>
</html>$HTML$,
 75,
 162,
 1120,
 false,
 0,
 NOW(),
 '{"name": "板块运动", "description": "地球板块的运动、碰撞和分离过程", "difficulty": "hard", "render_mode": "html"}');

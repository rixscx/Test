from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def eden_purple_theme_status(request):
    """
    Returns the "AEGIS OS" with corrected, high-visibility ASCII art.
    """

    # --- CORRECTED ASCII ART ---
    # Replaced with solid block characters for maximum visibility.
    eden_art = """
███████╗██████╗ ███████╗███╗   ██╗
██╔════╝██╔══██╗██╔════╝████╗  ██║
█████╗  ██║  ██║█████╗  ██╔██╗ ██║
██╔══╝  ██║  ██║██╔══╝  ██║╚██╗██║
███████╗██████╔╝███████╗██║ ╚████║
╚══════╝╚═════╝ ╚══════╝╚═╝  ╚═══╝
"""
    backend_art = """
██████╗ █████╗  ███████╗██╗   ██╗███████╗███╗   ██╗██████╗ 
██╔══██╗██╔══██╗██╔════╝██║   ██║██╔════╝████╗  ██║██╔══██╗
██████╔╝███████║█████╗  ███████║█████╗  ██╔██╗ ██║██║  ██║
██╔══██╗██╔══██║██╔══╝  ██╔══██║██╔══╝  ██║╚██╗██║██║  ██║
██████╔╝██║  ██║███████╗██║   ██║███████╗██║ ╚████║██████╔╝
╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝   ╚═╝╚══════╝╚═╝  ╚═══╝╚═════╝ 
"""

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AEGIS OS</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

            :root {{
                --background: #000000;
                --window-bg: rgba(5, 5, 5, 0.85);
                --accent-red: #FF003C;
                --accent-white: #FFFFFF;
                --font-primary: 'Share Tech Mono', monospace;
            }}

            * {{ box-sizing: border-box; margin: 0; padding: 0; }}

            body {{
                font-family: var(--font-primary);
                background-color: var(--background);
                color: var(--accent-white);
                overflow: hidden;
            }}
            
            #digital-rain-canvas {{
                position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 1;
            }}
            
            .os-container, .loader-wrapper {{
                display: flex; flex-direction: column; justify-content: center; align-items: center;
                height: 100vh;
                width: 100%;
            }}
            
            /* --- Loader --- */
            .loader-wrapper {{ z-index: 10; color: var(--accent-white); }}
            #loader-log-container {{
                width: 500px;
                border: 1px solid var(--accent-red);
                padding: 15px;
                background: rgba(0,0,0,0.8);
            }}
            #loader-log {{ font-size: 1rem; height: 150px; overflow: hidden; margin-bottom: 15px; }}
            .progress-bar {{ height: 4px; width: 100%; background-color: rgba(255, 0, 60, 0.2); }}
            #progress {{
                width: 0%; height: 100%; background: var(--accent-red);
                box-shadow: 0 0 10px var(--accent-red);
                transition: width 0.5s;
            }}

            /* --- Main OS --- */
            #os-container {{ display: none; }}
            
            .window {{
                position: absolute;
                background: var(--window-bg);
                border: 1px solid var(--accent-red);
                box-shadow: 0 0 20px rgba(255, 0, 60, 0.5);
                backdrop-filter: blur(10px);
                z-index: 5;
            }}
            .window-header {{
                background: var(--accent-red);
                color: var(--background);
                padding: 5px 10px;
                cursor: move;
                user-select: none;
            }}
            .window-body {{
                padding: 10px;
                background-image: linear-gradient(rgba(255, 0, 60, 0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 0, 60, 0.05) 1px, transparent 1px);
                background-size: 20px 20px;
            }}

            #ident-window {{ top: 5%; left: 5%; width: 550px; }}
            #ident-window pre {{
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 0.8em;
                line-height: 1.1; /* Adjusted for better spacing */
                opacity: 0;
                animation: textFlickerIn 1s forwards;
            }}
            #ident-window pre:last-child {{ animation-delay: 0.2s; }}


            #core-window {{ top: 5%; right: 5%; width: 250px; text-align: center; }}
            .avatar-container {{
                position: relative;
                overflow: hidden;
            }}
            #avatar {{
                max-width: 100%;
                height: auto;
                filter: drop-shadow(0 0 15px var(--accent-red));
                animation: pulse 4s infinite ease-in-out;
            }}
            .avatar-container::after {{ /* Scanline effect over avatar */
                content: '';
                position: absolute;
                top: 0; left: 0; width: 100%; height: 3px;
                background: rgba(0,0,0,0.5);
                box-shadow: 0 0 10px var(--accent-red);
                animation: scanline 3s linear infinite;
                
            }}

            #network-window {{ top: 40%; left: 5%; width: 550px; }}
            .endpoint-item {{ display: flex; justify-content: space-between; margin-bottom: 5px; }}
            .endpoint-status {{ color: var(--accent-red); }}
            .endpoint-status.secure {{ color: #00FF7F; }}

            #cli-container {{
                position: absolute;
                bottom: 0; left: 0; width: 100%;
                background: rgba(0,0,0,0.9);
                padding: 10px;
                border-top: 1px solid var(--accent-red);
                z-index: 10;
            }}
            #cli-output {{ height: 100px; overflow-y: scroll; margin-bottom: 10px; }}
            .cli-error {{ color: var(--accent-red); }}
            #cli-input-line {{ display: flex; }}
            #cli-input {{
                flex-grow: 1; background: none; border: none;
                color: var(--accent-white); font-family: var(--font-primary);
                font-size: 1rem;
            }}
            #cli-input:focus {{ outline: none; }}
            .cursor {{
                width: 10px; height: 1.2rem;
                background: var(--accent-white);
                animation: blink 1s step-end infinite;
            }}

            @keyframes blink {{ 50% {{ opacity: 0; }} }}
            @keyframes pulse {{ 50% {{ opacity: 0.8; filter: drop-shadow(0 0 25px var(--accent-red)); }} }}
            @keyframes scanline {{ from {{ top: -10px; }} to {{ top: 110%; }} }}
            @keyframes textFlickerIn {{
                0% {{ opacity: 0; text-shadow: 0 0 20px var(--accent-red); }}
                50% {{ opacity: 1; text-shadow: 0 0 5px var(--accent-red); }}
                100% {{ opacity: 1; text-shadow: none; }}
            }}
        </style>
    </head>
    <body>
        <canvas id="digital-rain-canvas"></canvas>

        <div class="loader-wrapper" id="loader">
            <div id="loader-log-container">
                <div id="loader-log"></div>
                <div class="progress-bar"><div id="progress"></div></div>
            </div>
        </div>

        <div id="os-container">
            <div id="ident-window" class="window">
                <div class="window-header">[ IDENTIFICATION_SIG ]</div>
                <div class="window-body">
                    <pre>{eden_art}</pre>
                    <div style="height: 10px;"></div>
                    <pre>{backend_art}</pre>
                </div>
            </div>

            <div id="core-window" class="window">
                <div class="window-header">[ AEGIS_CORE :: COMMS ]</div>
                <div class="window-body">
                    <div class="avatar-container">
                        <img id="avatar" src="https://img.freepik.com/premium-psd/scary-skull-aigenerated_980077-4542.jpg" alt="AEGIS Avatar">
                    </div>
                </div>
            </div>
            
            <div id="network-window" class="window">
                <div class="window-header">[ NETWORK_RELAY ]</div>
                <div class="window-body" id="network-body">
                    <div class="endpoint-item"><span class="path">/api/analyze/</span><span class="endpoint-status">[PENDING]</span></div>
                    <div class="endpoint-item"><span class="path">/api/recipes/</span><span class="endpoint-status">[PENDING]</span></div>
                    <div class="endpoint-item"><span class="path">/api/guestbook/</span><span class="endpoint-status">[PENDING]</span></div>
                    <div class="endpoint-item"><span class="path">/api/user/</span><span class="endpoint-status">[PENDING]</span></div>
                    <div class="endpoint-item"><span class="path">/api/chatbot/</span><span class="endpoint-status">[PENDING]</span></div>
                </div>
            </div>

            <div id="cli-container">
                <div id="cli-output"></div>
                <div id="cli-input-line">
                    <span>> </span>
                    <input type="text" id="cli-input" autofocus autocomplete="off" placeholder="Enter command... (type 'help' for options)">
                    <div class="cursor"></div>
                </div>
            </div>
        </div>
        
        <audio id="main-audio" loop preload="auto"><source src="/static/load.mp3" type="audio/mpeg"></audio>

        <script>
            // --- Audio ---
            const mainAudio = document.getElementById('main-audio');
            let soundInitialized = false;
            
            // --- Loader ---
            const loaderLog = document.getElementById('loader-log');
            const progressBar = document.getElementById('progress');
            const bootSequence = [
                {{ text: "AEGIS OS BOOTSTRAP...", duration: 500, progress: 15 }},
                {{ text: "LOADING KERNEL...", duration: 800, progress: 40 }},
                {{ text: "VERIFYING SIGNATURES...", duration: 700, progress: 75 }},
                {{ text: "SYSTEM ONLINE. Welcome Operator.", duration: 600, progress: 100 }}
            ];
            let bootIndex = 0;
            
            function runBoot() {{
                if (bootIndex >= bootSequence.length) {{
                    document.getElementById('loader').style.display = 'none';
                    document.getElementById('os-container').style.display = 'flex';
                    document.getElementById('cli-input').focus();
                    return;
                }}
                const step = bootSequence[bootIndex];
                loaderLog.innerHTML += `<div>> ${{step.text}}</div>`;
                loaderLog.scrollTop = loaderLog.scrollHeight;
                progressBar.style.width = step.progress + '%';
                bootIndex++;
                setTimeout(runBoot, step.duration);
            }}
            
            runBoot();

            // --- CLI ---
            const cliInput = document.getElementById('cli-input');
            const cliOutput = document.getElementById('cli-output');
            cliInput.addEventListener('keydown', function(e) {{
                if (e.key === 'Enter') {{
                    if (!soundInitialized) {{
                        mainAudio.volume = 0.5;
                        soundInitialized = true;
                        mainAudio.play().then(() => mainAudio.pause());
                    }}

                    const command = this.value.trim().toLowerCase();
                    output(`> ${{command}}`);
                    handleCommand(command);
                    this.value = '';
                }}
            }});
            function handleCommand(cmd) {{
                const commands = {{
                    'help': "Commands: help, status, scan, sysinfo, clear, jam, chill",
                    'status': 'All systems nominal. AEGIS Core running at 100%.',
                    'sysinfo': `OS: AEGIS v3.1<br>Core: Quantum Entanglement Processor<br>Memory: 65536MB`,
                    'clear': () => cliOutput.innerHTML = '',
                    'scan': () => scanEndpoints(),
                    'jam': () => {{
                        if (!soundInitialized) {{
                            output(`<span class="cli-error">Audio system not ready. Type any command once to initialize.</span>`);
                            return;
                        }}
                        mainAudio.play().catch(e => output(`<span class="cli-error">Playback failed.</span>`));
                        output('Now Playing: load.mp3');
                    }},
                    'chill': () => {{
                        mainAudio.pause();
                        mainAudio.currentTime = 0;
                        output('Audio Playback Stopped.');
                    }}
                }};
                
                const response = commands[cmd];
                if (response) {{
                     if (typeof response === 'function') response(); else output(response);
                }} else {{
                    output(`<span class="cli-error">Error: Command not found '${{cmd}}'</span>`);
                }}
            }}
            
            function output(message) {{ cliOutput.innerHTML += `<div>${{message}}</div>`; cliOutput.scrollTop = cliOutput.scrollHeight; }}
            function scanEndpoints() {{
                const statuses = document.querySelectorAll('.endpoint-status');
                statuses.forEach((status, i) => {{
                    setTimeout(() => {{
                        status.textContent = '[SCANNING...]';
                        setTimeout(() => {{ status.textContent = '[SECURE]'; status.classList.add('secure'); }}, 500);
                    }}, i * 200);
                }});
                output('Network scan complete. 5 secure connections established.');
            }}

            // --- Draggable Windows ---
            document.querySelectorAll('.window').forEach(win => {{
                let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
                win.querySelector('.window-header').onmousedown = e => {{
                    e.preventDefault(); pos3 = e.clientX; pos4 = e.clientY;
                    document.onmouseup = () => {{ document.onmouseup = null; document.onmousemove = null; }};
                    document.onmousemove = ev => {{
                        ev.preventDefault();
                        pos1 = pos3 - ev.clientX; pos2 = pos4 - ev.clientY;
                        pos3 = ev.clientX; pos4 = ev.clientY;
                        win.style.top = (win.offsetTop - pos2) + "px";
                        win.style.left = (win.offsetLeft - pos1) + "px";
                    }};
                }};
            }});

            // --- Digital Rain ---
            const canvas = document.getElementById('digital-rain-canvas');
            const ctx = canvas.getContext('2d');
            canvas.width = window.innerWidth; canvas.height = window.innerHeight;
            const katakana = 'アァカサタナハマヤャラワガザダバパイキシチニヒミリヰギジヂビピウクスツヌフムユルグズブプエケセテネヘメレオコソトノホモヨロヲゴゾドボポヴッン';
            const latin = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
            const nums = '0123456789';
            const alphabet = katakana + latin + nums;
            const fontSize = 16;
            const columns = canvas.width / fontSize;
            const rainDrops = Array.from({{ length: Math.ceil(columns) }}).fill(1);
            function drawRain() {{
                ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.font = fontSize + 'px monospace';
                for (let i = 0; i < rainDrops.length; i++) {{
                    ctx.fillStyle = Math.random() > 0.995 ? '#FF003C' : '#FFFFFF';
                    const text = alphabet.charAt(Math.floor(Math.random() * alphabet.length));
                    ctx.fillText(text, i * fontSize, rainDrops[i] * fontSize);
                    if (rainDrops[i] * fontSize > canvas.height && Math.random() > 0.975) rainDrops[i] = 0;
                    rainDrops[i]++;
                }}
            }}
            setInterval(drawRain, 33);
        </script>
    </body>
    </html>
    """
    return HttpResponse(html_content)

urlpatterns = [
    path('', eden_purple_theme_status),
    path('admin/', admin.site.urls),
    path('api/analyze/', include('analyzer.urls')),
    path('api/recipes/', include('analyzer.urls')),
    path('api/guestbook/', include('guestbook.urls')),
    path('accounts/', include('allauth.urls')),
    path('api/user/', include('guestbook.user_urls')),
    path('api/chatbot/', include('chatbot.urls')),
]
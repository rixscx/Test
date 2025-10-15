from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def eden_purple_theme_status(request):
    """
    Returns a refined, cyberpunk-themed status page with a live 'Matrix'
    background and a green/cyan color scheme.
    """

    # ASCII art for "EDEN"
    eden_art = """
███████╗██████╗ ███████╗███╗   ██╗
██╔════╝██╔══██╗██╔════╝████╗  ██║
█████╗  ██║  ██║█████╗  ██╔██╗ ██║
██══╝  ██║  ██║██╔══╝  ██║╚██╗██║
███████╗██████╔╝███████╗██║ ╚████║
╚══════╝╚═════╝ ╚══════╝╚═╝  ╚═══╝
"""

    # ASCII art for "BACKEND"
    backend_art = """
██████╗ █████╗  ███████╗██╗   ██╗███████╗███╗   ██╗██████╗
██╔══██╗██╔══██╗██╔════╝██║   ██║██╔════╝████╗  ██║██╔══██╗
██████╔╝███████║█████╗  ███████║█████╗  ██╔██╗ ██║██║  ██║
██╔══██╗██╔══██║██══╝  ██╔══██║██╔══╝  ██║╚██╗██║██║  ██║
██████╔╝██║  ██║███████╗██║   ██║███████╗██║ ╚████║██████╔╝
╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝   ╚═╝╚══════╝╚═╝  ╚═══╝╚═════╝
"""

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EDEN :: SYSTEM KERNEL</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

            :root {{
                --background: #010409;
                --terminal-bg: rgba(10, 0, 20, 0.92); 
                --accent-cyan: #00e5ff;
                /* Replaced magenta with a vibrant green */
                --accent-green: #39FF14; 
                --text-color: #f0f0f0;
                --font-primary: 'Share Tech Mono', monospace;
            }}

            * {{
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }}

            body {{
                font-family: var(--font-primary);
                background-color: var(--background);
                color: var(--text-color);
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 100vh;
                overflow: hidden;
            }}

            #matrix-canvas {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 1;
            }}

            .terminal-container {{
                position: relative;
                z-index: 2;
                width: 90%;
                max-width: 950px;
                background: var(--terminal-bg);
                /* Updated border and shadow to use the new green accent */
                border: 1px solid var(--accent-green);
                border-radius: 8px;
                box-shadow: 0 0 15px rgba(57, 255, 20, 0.5); /* Green shadow */
                backdrop-filter: blur(5px);
                padding: 25px;
                animation: fadeIn 1s ease-out;
            }}

            .ascii-art-wrapper {{
                text-align: center;
                margin-bottom: 25px;
                animation: fadeIn 1.5s ease-out;
            }}

            .ascii-art {{
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 0.85em;
                line-height: 1.0;
                color: #FFFFFF; 
                white-space: pre;
                margin: 0;
            }}

            .status-line {{
                border-top: 1px dashed var(--accent-cyan);
                padding-top: 20px;
                margin-top: 20px;
                font-size: 1.25rem;
                white-space: nowrap;
                overflow: hidden;
                width: 31ch;
                margin-left: auto;
                margin-right: auto;
                animation: 
                    typing 3.5s steps(31), 
                    blink-caret .5s step-end infinite alternate;
                border-right: 3px solid var(--text-color);
            }}

            .api-map {{
                border-top: 1px dashed var(--accent-cyan);
                padding-top: 20px;
                margin-top: 25px;
                text-align: center;
            }}
            
            .api-map h3 {{
                font-size: 1.3rem;
                margin-bottom: 15px;
                letter-spacing: 2px;
                color: var(--text-color);
            }}
            
            .api-map ul {{
                list-style: none;
            }}
            
            .api-map li {{
                margin: 10px 0;
                font-size: 1.15rem;
                opacity: 0;
                transform: translateY(10px);
                animation: slideInItem 0.5s forwards;
            }}
            
            .api-map li:nth-child(1) {{ animation-delay: 1.5s; }}
            .api-map li:nth-child(2) {{ animation-delay: 1.7s; }}
            .api-map li:nth-child(3) {{ animation-delay: 1.9s; }}
            .api-map li:nth-child(4) {{ animation-delay: 2.1s; }}
            .api-map li:nth-child(5) {{ animation-delay: 2.3s; }}
            
            .api-map .method {{
                /* Updated method color to green */
                color: var(--accent-green);
                font-weight: bold;
                margin-right: 15px;
            }}
            
            .api-map .path {{
                color: var(--accent-cyan);
            }}

            /* --- KEYFRAMES --- */
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: scale(0.98); }}
                to {{ opacity: 1; transform: scale(1); }}
            }}
            @keyframes typing {{
                from {{ width: 0; }}
            }}
            @keyframes blink-caret {{
                50% {{ border-color: transparent; }}
            }}
            @keyframes slideInItem {{
                to {{ opacity: 1; transform: translateY(0); }}
            }}
        </style>
    </head>
    <body>
        <canvas id="matrix-canvas"></canvas>

        <div class="terminal-container">
            <div class="ascii-art-wrapper">
                <pre class="ascii-art">{eden_art}</pre>
                <div style="height: 15px;"></div>
                <pre class="ascii-art">{backend_art}</pre>
            </div>

            <p class="status-line">>&nbsp;SYSTEM KERNEL: [ONLINE]</p>

            <div class="api-map">
                <h3>[ SERVICE ENDPOINTS ]</h3>
                <ul>
                    <li><span class="method">GET</span><span class="path">/api/analyze/</span></li>
                    <li><span class="method">GET</span><span class="path">/api/recipes/</span></li>
                    <li><span class="method">GET</span><span class="path">/api/guestbook/</span></li>
                    <li><span class="method">POST</span><span class="path">/api/user/</span></li>
                    <li><span class="method">POST</span><span class="path">/api/chatbot/</span></li>
                </ul>
            </div>
        </div>

        <script>
            const canvas = document.getElementById('matrix-canvas');
            const ctx = canvas.getContext('2d');
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            const alphabet = 'アァカサタナハマヤャラワガザダバパイキシチニヒミリヰギジヂビピウクスツヌフムユルグズブプエケセテネヘメレオコソトノホモヨロヲゴゾドボポヴッン0123456789';
            const fontSize = 16;
            const columns = canvas.width / fontSize;
            const rainDrops = Array.from({{ length: columns }}).fill(1);

            const draw = () => {{
                ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = '#00e5ff';
                ctx.font = fontSize + 'px monospace';
                for (let i = 0; i < rainDrops.length; i++) {{
                    const text = alphabet.charAt(Math.floor(Math.random() * alphabet.length));
                    ctx.fillText(text, i * fontSize, rainDrops[i] * fontSize);
                    if (rainDrops[i] * fontSize > canvas.height && Math.random() > 0.975) {{
                        rainDrops[i] = 0;
                    }}
                    rainDrops[i]++;
                }}
            }};

            setInterval(draw, 33);
            
            window.addEventListener('resize', () => {{
                canvas.width = window.innerWidth;
                canvas.height = window.innerHeight;
            }});
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
# Rendu image par image du réel : python3 render.py <chemin_reel.html> <dossier_frames> <duree_s>
import asyncio, sys, pathlib
from playwright.async_api import async_playwright
html, out, D = pathlib.Path(sys.argv[1]).resolve(), pathlib.Path(sys.argv[2]), float(sys.argv[3]); FPS=25
out.mkdir(parents=True, exist_ok=True)
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1080,'height':1920})
        await pg.goto(html.as_uri()); await pg.wait_for_timeout(500)
        for i in range(int(FPS*D)):
            await pg.evaluate(f'render({i/FPS})')
            await pg.screenshot(path=str(out/f'f{i:04d}.jpg'),type='jpeg',quality=92)
        await b.close()
asyncio.run(main())

# -*- coding: utf-8 -*-
"""Verify PawApp SDK migration in p_plugin_main.py"""
import sys, os
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', encoding='utf-8', closefd=False)

f = open(os.path.join(os.path.dirname(__file__), 'p_plugin_main.py'), 'r', encoding='utf-8').read()
lines = f.splitlines()

# Find version
for l in lines:
    if 'CURRENT_VERSION' in l:
        # print raw repr for debugging
        pass

sse_routes = sum(1 for l in lines if '@app.route' in l)
app_tools = sum(1 for l in lines if '@app.tool' in l)

print(f"Total lines: {len(lines)}")
print(f"PawApp(name=…): {'PawApp(name=' in f}")
print(f"router = APIRouter(): {'router = APIRouter()' in f}")
print(f"app.include_router(router): {'app.include_router(router)' in f}")
print(f"@app.on_launch: {'@app.on_launch' in f}")
print(f"@app.on_terminate: {'@app.on_terminate' in f}")
print(f"SSE routes (@app.route): {sse_routes}")
print(f"PawApp tools (@app.tool): {app_tools}")
print(f"broadcast_via_sse: {'async def broadcast_via_sse' in f}")
print(f"plugin = app: {'plugin = app' in f}")
print(f"Depends(get_ctx): {'Depends(get_ctx)' in f}")
print(f"Legacy PPlugin class: {'class PPlugin' in f}")
print(f"Legacy get_router(): {'def get_router' in f}")
print(f"SSEChannel import: {'SSEChannel' in f}")
print(f"PawAppContext import: {'PawAppContext' in f}")
print(f"from _pawapp_compat: {'from ._pawapp_compat' in f}")
print()
print("=== PawApp SDK Migration Summary ===")

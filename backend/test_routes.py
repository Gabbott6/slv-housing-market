"""
Test script to verify all routes are properly registered.
Run this to diagnose routing issues.
"""
import sys
from app.main import app

print("="*60)
print("ROUTE REGISTRATION TEST")
print("="*60)

print(f"\nTotal routes registered: {len(app.routes)}")

print("\n--- Property AI Routes ---")
ai_routes = [r for r in app.routes if hasattr(r, 'path') and 'property-ai' in r.path]
if ai_routes:
    for route in ai_routes:
        methods = route.methods if hasattr(route, 'methods') else ['N/A']
        print(f"  {list(methods)} {route.path}")
else:
    print("  ❌ NO PROPERTY-AI ROUTES FOUND!")

print("\n--- All API Routes ---")
api_routes = [r for r in app.routes if hasattr(r, 'path') and r.path.startswith('/api/')]
for route in sorted(api_routes, key=lambda r: r.path):
    methods = route.methods if hasattr(route, 'methods') else ['N/A']
    print(f"  {list(methods)} {route.path}")

print("\n" + "="*60)
print("If property-ai routes show here but not in running server,")
print("the issue is with uvicorn caching, not the code.")
print("="*60)

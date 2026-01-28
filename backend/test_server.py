"""
Test script to verify routes are correctly loaded.
"""
import uvicorn
from app.main import app

# Print all routes
print("\n" + "="*60)
print("REGISTERED ROUTES")
print("="*60)

for route in app.routes:
    if hasattr(route, 'path') and route.path.startswith('/api/'):
        methods = route.methods if hasattr(route, 'methods') else ['N/A']
        print(f"{list(methods)} {route.path}")

print("="*60)

# Check specifically for property-ai routes
property_ai_routes = [r for r in app.routes if hasattr(r, 'path') and 'property-ai' in r.path]
print(f"\nFound {len(property_ai_routes)} property-ai routes")

if len(property_ai_routes) > 0:
    print("\n[OK] All routes loaded correctly!")
    print("\nStarting server...\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
else:
    print("\n[ERROR] Property-AI routes NOT found!")
    print("Something is wrong with the router registration.")

#!/usr/bin/env python3
"""
Patch script to fix MongoDB ObjectId JSON serialization issues.
This script should be copied into the running container and executed there.
"""

import os
import json
from bson import ObjectId

# Define the MongoJSONEncoder class
ENCODER_CODE = """
# Create a custom JSON encoder for MongoDB ObjectId
class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)  # Convert ObjectId to string
        return super().default(obj)
"""

# Define the patches to apply
PATCHES = [
    {
        "file": "/app/fastapiServer.py",
        "imports": "from bson import ObjectId  # Import ObjectId from bson",
        "define_encoder": ENCODER_CODE,
        "replacements": [
            {
                "old": "with open(log_path, \"a\", encoding=\"utf-8\") as log_file:\n        log_file.write(json.dumps(log_entry, ensure_ascii=False) + \"\\n\")",
                "new": "with open(log_path, \"a\", encoding=\"utf-8\") as log_file:\n        log_file.write(json.dumps(log_entry, ensure_ascii=False, cls=MongoJSONEncoder) + \"\\n\")"
            },
            {
                "old": "SaveFile(savepath, json.dumps(json_data, ensure_ascii=False, indent=4))",
                "new": "SaveFile(savepath, json.dumps(json_data, ensure_ascii=False, indent=4, cls=MongoJSONEncoder))"
            },
            {
                "old": "return JSONResponse(content=logs)",
                "new": "return JSONResponse(content=json.loads(json.dumps(logs, cls=MongoJSONEncoder)))"
            },
            {
                "old": "return JSONResponse(content=articles)",
                "new": "return JSONResponse(content=json.loads(json.dumps(articles, cls=MongoJSONEncoder)))"
            }
        ]
    }
]

def apply_patch(file_path, imports, define_encoder, replacements):
    """Apply patches to a file"""
    print(f"Patching {file_path}...")
    
    # Read the current content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add imports after the last import line
    import_pos = content.rfind('import ')
    import_line_end = content.find('\n', import_pos)
    if import_pos != -1 and import_line_end != -1:
        content = content[:import_line_end + 1] + imports + '\n' + content[import_line_end + 1:]
    
    # Add encoder definition after imports but before the first function or class
    first_def = content.find('def ')
    first_class = content.find('class ')
    insert_pos = min(first_def, first_class) if first_def != -1 and first_class != -1 else max(first_def, first_class)
    if insert_pos != -1:
        # Find the last line break before this position
        last_break = content.rfind('\n\n', 0, insert_pos)
        if last_break != -1:
            content = content[:last_break + 2] + define_encoder + '\n\n' + content[last_break + 2:]
    
    # Apply the replacements
    for replacement in replacements:
        content = content.replace(replacement['old'], replacement['new'])
    
    # Write the updated content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Successfully patched {file_path}")

def main():
    """Main function to apply all patches"""
    for patch in PATCHES:
        apply_patch(
            patch['file'],
            patch['imports'],
            patch['define_encoder'],
            patch['replacements']
        )
    
    print("\nAll patches applied successfully!")
    print("Restart the FastAPI application for changes to take effect.")

if __name__ == "__main__":
    main() 
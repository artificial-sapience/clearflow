# Step-by-Step Guide: Implementing llms.txt Files for ClearFlow

## Prerequisites

- Python 3.9+ installed
- Git repository at <https://github.com/artificial-sapience/ClearFlow>
- Write access to the repository

## Phase 1: Create the Minimal llms.txt File

### Step 1.1: Create llms.txt in Repository Root

**Location**: `/llms.txt` (repository root, same level as README.md)

### Step 1.2: Write the Content

Create the file with this exact structure:

```markdown
# ClearFlow

> Type-safe orchestration for unpredictable AI - A Python library that provides robust, immutable state management and explicit routing for building reliable AI workflows with 100% test coverage and zero dependencies.

## Documentation

- [README](https://raw.githubusercontent.com/artificial-sapience/ClearFlow/main/README.md): Complete overview and quickstart guide
- [API Reference](https://raw.githubusercontent.com/artificial-sapience/ClearFlow/main/clearflow/__init__.py): Core module exports and type definitions
- [Node Implementation](https://raw.githubusercontent.com/artificial-sapience/ClearFlow/main/clearflow/node.py): Node base class and NodeResult implementation
- [Flow Builder](https://raw.githubusercontent.com/artificial-sapience/ClearFlow/main/clearflow/flow.py): Flow construction and routing logic
- [Exceptions](https://raw.githubusercontent.com/artificial-sapience/ClearFlow/main/clearflow/exceptions.py): Custom exception definitions

## Examples

- [Portfolio Analysis](https://raw.githubusercontent.com/artificial-sapience/ClearFlow/main/examples/portfolio_analysis.py): Financial data processing with type-safe transformations
- [RAG Pipeline](https://raw.githubusercontent.com/artificial-sapience/ClearFlow/main/examples/rag.py): Retrieval-augmented generation workflow implementation

## Testing

- [Test Suite](https://raw.githubusercontent.com/artificial-sapience/ClearFlow/main/tests/test_flow.py): Comprehensive test coverage demonstrating all patterns
- [Node Tests](https://raw.githubusercontent.com/artificial-sapience/ClearFlow/main/tests/test_node.py): Unit tests for Node behavior

## Optional

- [Migration Guide](https://raw.githubusercontent.com/artificial-sapience/ClearFlow/main/MIGRATION.md): Upgrading from v0.x to v1.x
- [Contributing](https://raw.githubusercontent.com/artificial-sapience/ClearFlow/main/CONTRIBUTING.md): Contribution guidelines
- [License](https://raw.githubusercontent.com/artificial-sapience/ClearFlow/main/LICENSE): MIT License
```

### Step 1.3: Validate the Format

Ensure:

- ✅ Starts with `# ProjectName` (H1 header)
- ✅ Has `> Summary` blockquote on next line
- ✅ Uses `## SectionName` for each section (H2 headers)
- ✅ Each link format: `- [Title](URL): Description`
- ✅ All URLs use `https://raw.githubusercontent.com/` for raw content
- ✅ File is under 5KB (should be ~2KB)

## Phase 2: Set Up Tooling for llms-full.txt

### Step 2.1: Install the llms-txt Package

```bash
pip install llms-txt
```

Or add to your development dependencies:

```bash
uv add --dev llms-txt
```

### Step 2.2: Create a Generation Script

Create `scripts/generate_llms_full.py`:

```python
#!/usr/bin/env python3
"""Generate llms-full.txt from llms.txt"""

import subprocess
import sys
from pathlib import Path

def main():
    # Get project root
    project_root = Path(__file__).parent.parent
    llms_txt_path = project_root / "llms.txt"
    llms_full_path = project_root / "llms-full.txt"
    
    # Check if llms.txt exists
    if not llms_txt_path.exists():
        print(f"Error: {llms_txt_path} not found")
        sys.exit(1)
    
    # Generate llms-full.txt using llms_txt2ctx
    try:
        result = subprocess.run(
            ["llms_txt2ctx", "--optional", str(llms_txt_path)],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Write the output to llms-full.txt
        llms_full_path.write_text(result.stdout)
        print(f"Successfully generated {llms_full_path}")
        
    except subprocess.CalledProcessError as e:
        print(f"Error generating llms-full.txt: {e}")
        print(f"stderr: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: llms_txt2ctx not found. Install with: pip install llms-txt")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### Step 2.3: Make Script Executable

```bash
chmod +x scripts/generate_llms_full.py
```

## Phase 3: Generate llms-full.txt

### Step 3.1: Run the Generation Script

```bash
python scripts/generate_llms_full.py
```

### Step 3.2: Alternative Manual Generation

If the script doesn't work, use the command line directly:

```bash
llms_txt2ctx --optional llms.txt > llms-full.txt
```

### Step 3.3: Verify the Output

The generated `llms-full.txt` should:

- Be an XML-structured document
- Include all content from linked files
- Be significantly larger (likely 50-200KB)
- Start with `<project title="ClearFlow"...>`

## Phase 4: Add to Version Control

### Step 4.1: Update .gitignore (Optional)

Consider whether to track llms-full.txt or generate it dynamically:

**Option A - Track Both Files:**

```bash
git add llms.txt llms-full.txt
git commit -m "Add llms.txt files for AI assistant compatibility"
```

**Option B - Generate llms-full.txt Dynamically:**
Add to `.gitignore`:

```text
llms-full.txt
```

Then only commit llms.txt:

```bash
git add llms.txt scripts/generate_llms_full.py
git commit -m "Add llms.txt and generation script"
```

## Phase 5: Add CI/CD Integration (Optional)

### Step 5.1: Create GitHub Action

Create `.github/workflows/update-llms.yml`:

```yaml
name: Update llms-full.txt

on:
  push:
    branches: [main]
    paths:
      - 'llms.txt'
      - 'clearflow/**'
      - 'examples/**'
      - 'README.md'

jobs:
  update-llms:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install llms-txt
        run: pip install llms-txt
      
      - name: Generate llms-full.txt
        run: llms_txt2ctx --optional llms.txt > llms-full.txt
      
      - name: Commit changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add llms-full.txt
          git diff --quiet && git diff --staged --quiet || git commit -m "Update llms-full.txt"
          git push
```

## Phase 6: Testing and Validation

### Step 6.1: Test with curl

```bash
# Test llms.txt accessibility
curl https://raw.githubusercontent.com/artificial-sapience/ClearFlow/main/llms.txt

# Test llms-full.txt (if committed)
curl https://raw.githubusercontent.com/artificial-sapience/ClearFlow/main/llms-full.txt
```

### Step 6.2: Validate with Online Tools

- Visit <https://llmstxtvalidator.dev/>
- Paste your llms.txt content
- Check for any validation errors

### Step 6.3: Test with AI Assistants

1. **Claude Projects**: Add the llms-full.txt URL as a project resource
2. **Cursor**: Use @doc and add the llms.txt URL
3. **GitHub Copilot**: The files will be automatically detected

## Phase 7: Register and Maintain

### Step 7.1: Submit to llms-txt Hub

1. Visit <https://github.com/thedaviddias/llms-txt-hub>
2. Fork the repository
3. Add ClearFlow entry to the appropriate category
4. Submit a pull request

### Step 7.2: Set Up Maintenance Schedule

- Review quarterly (every 3 months)
- Update when:
  - Major API changes occur
  - New examples are added
  - Documentation structure changes
  - File paths change

### Step 7.3: Create Update Checklist

Add to `CONTRIBUTING.md`:

```markdown
## Updating llms.txt Files

When making significant changes:
- [ ] Update llms.txt if new documentation files are added
- [ ] Regenerate llms-full.txt using `python scripts/generate_llms_full.py`
- [ ] Verify all URLs in llms.txt are valid
- [ ] Test with an AI assistant to ensure proper understanding
```

## Quick Command Summary

```bash
# One-time setup
pip install llms-txt

# Create llms.txt (manually create the file with content above)
echo "Creating llms.txt..."
# [Add the content from Step 1.2]

# Generate llms-full.txt
llms_txt2ctx --optional llms.txt > llms-full.txt

# Commit both files
git add llms.txt llms-full.txt
git commit -m "Add llms.txt files for AI assistant compatibility"
git push
```

## Troubleshooting

### Common Issues and Solutions

1. **llms_txt2ctx command not found**
   - Solution: `pip install llms-txt`

2. **URLs returning 404**
   - Verify branch name (main vs master)
   - Ensure files exist at specified paths
   - Use raw.githubusercontent.com URLs

3. **llms-full.txt too large for context**
   - This is expected for large projects
   - AI assistants will chunk and index automatically
   - Consider creating topic-specific llms.txt files

4. **Validation errors**
   - Ensure H1 title is present
   - Check blockquote formatting (> symbol)
   - Verify markdown link syntax

## Success Criteria

✅ llms.txt exists at repository root
✅ File validates at llmstxtvalidator.dev
✅ All linked URLs are accessible
✅ llms-full.txt generates without errors
✅ AI assistants can understand ClearFlow's architecture
✅ File sizes: llms.txt < 5KB, llms-full.txt < 500KB

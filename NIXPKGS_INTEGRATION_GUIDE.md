# 🚀 Nixpkgs Integration Guide for langgraph-runtime-inmem-open

This guide follows the **official Nixpkgs contribution standards** to integrate your open-source alternative into the Nixpkgs repository, solving the supply-chain security issue.

**Official Reference**: [Nixpkgs Contributing Guide](https://github.com/NixOS/nixpkgs/blob/master/CONTRIBUTING.md)

## 📋 **Prerequisites**

1. **GitHub Account** - You already have this
2. **Fork of nixpkgs** - You'll need to create this
3. **Nix installed** - For testing locally (optional)

## 🔧 **Step-by-Step Integration (Following Official Standards)**

### **Step 1: Fork and Setup Nixpkgs Repository**

1. **Fork the Nixpkgs repository**:
   - Go to: https://github.com/NixOS/nixpkgs
   - Click "Fork" in the top right corner
   - Wait for the fork to complete

2. **Clone your forked repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/nixpkgs.git
   cd nixpkgs
   ```

3. **Configure the upstream repository**:
   ```bash
   git remote add upstream https://github.com/NixOS/nixpkgs.git
   ```

### **Step 2: Select Base Branch and Create Feature Branch**

**Important**: Most changes should go to `master`. Since this is a new package addition, we'll use `master`.

```bash
# Fetch latest changes from upstream
git fetch upstream

# Create and switch to a new branch based on master
git switch --create add-langgraph-runtime-inmem-open upstream/master
```

**Note**: If you want to avoid downloading many derivations, you can base on a specific commit:
- Latest nixpkgs-unstable: https://channels.nixos.org/nixpkgs-unstable
- Or use: `nix-instantiate --eval --expr '(import <nixpkgs/lib>).trivial.revisionWithDefault null'`

### **Step 3: Add the Package Definition**

1. **Create the package file**:
   ```bash
   mkdir -p pkgs/development/python-modules
   ```

2. **Add the package definition** to `pkgs/development/python-modules/langgraph-runtime-inmem-open.nix`:
   ```nix
   { lib
   , python3
   , fetchFromGitHub
   }:

   python3.pkgs.buildPythonPackage rec {
     pname = "langgraph-runtime-inmem-open";
     version = "0.1.0";

     src = fetchFromGitHub {
       owner = "AbdulmalikDS";
       repo = "langgraph-runtime-inmem-open";
       rev = "v${version}";
       sha256 = "sha256-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="; # Will be updated
     };

     format = "pyproject";

     propagatedBuildInputs = with python3.pkgs; [
       langgraph
       pydantic
     ];

     nativeBuildInputs = with python3.pkgs; [
       setuptools
       wheel
     ];

     checkInputs = with python3.pkgs; [
       pytest
       pytest-cov
       pytest-asyncio
       flake8
       black
       isort
       mypy
       pylint
     ];

     pythonImportsCheck = [ "langgraph_runtime_inmem_open" ];

     doCheck = true;

     meta = with lib; {
       description = "Open-source alternative to langgraph-runtime-inmem";
       homepage = "https://github.com/AbdulmalikDS/langgraph-runtime-inmem-open";
       license = licenses.mit;
       maintainers = with maintainers; [ ];
       platforms = platforms.unix ++ platforms.darwin;
       broken = false;
     };
   }
   ```

### **Step 4: Update the Python Packages List**

Add your package to `pkgs/top-level/python-packages.nix`:

1. **Find the section** with other Python packages (around line 1000-2000)
2. **Add your package**:
   ```nix
   langgraph-runtime-inmem-open = callPackage ../development/python-modules/langgraph-runtime-inmem-open.nix { };
   ```

### **Step 5: Get the Correct SHA256 Hash**

You need to get the correct SHA256 hash for your GitHub repository:

```bash
# Install nix-prefetch-git if you don't have it
nix-env -iA nixpkgs.nix-prefetch-git

# Get the hash
nix-prefetch-git https://github.com/AbdulmalikDS/langgraph-runtime-inmem-open.git v0.1.0
```

**Copy the `sha256` value** and replace the placeholder in the package definition.

### **Step 6: Test the Package Locally**

```bash
# Test building the package
nix-build -A python3Packages.langgraph-runtime-inmem-open

# Test importing
nix-build -A python3Packages.langgraph-runtime-inmem-open.pythonImportsCheck
```

### **Step 7: Update langgraph-cli Package**

Find the `langgraph-cli` package definition and update it to use your open-source alternative:

```nix
# In the langgraph-cli package definition, replace:
# langgraph-runtime-inmem
# with:
langgraph-runtime-inmem-open
```

### **Step 8: Test Your Changes**

**Follow Nixpkgs testing standards**:

1. **Test with sandboxing enabled** (required):
   ```bash
   # Add to /etc/nix/nix.conf if not already there:
   # sandbox = true
   
   # Test the package
   nix-build -A python3Packages.langgraph-runtime-inmem-open
   ```

2. **Test compilation of dependent packages**:
   ```bash
   nix-shell -p nixpkgs-review --run "nixpkgs-review wip"
   ```

3. **Test execution of binaries** (if any):
   ```bash
   # Check if there are any executables
   ls ./result/bin/
   ```

### **Step 9: Commit Your Changes**

**Follow Nixpkgs commit conventions**:

```bash
# Format your Nix files
nix fmt

# Add your changes
git add .

# Commit with proper message format
git commit -m "python3Packages.langgraph-runtime-inmem-open: init at 0.1.0

Add open-source alternative to langgraph-runtime-inmem package.
This solves supply-chain security issues for Nixpkgs users.

- MIT licensed and fully auditable
- Same API as the original package
- Drop-in replacement for langgraph-cli[inmem]
- Comprehensive test suite with 19/19 tests passing

Closes: https://github.com/NixOS/nixpkgs/issues/430234"
```

### **Step 10: Push and Create Pull Request**

```bash
# Push your branch
git push --set-upstream origin HEAD
```

**GitHub will output a link to create the PR directly**:
```
remote: Create a pull request for 'add-langgraph-runtime-inmem-open' on GitHub by visiting:
remote:      https://github.com/YOUR_USERNAME/nixpkgs/pull/new/add-langgraph-runtime-inmem-open
```

### **Step 11: Fill in the Pull Request Template**

The PR will be pre-populated with checkboxes. **Make sure to check all that apply**:

## 📝 **Pull Request Template**

**Check these boxes in your PR**:

- [ ] **Tested using sandboxing** (Nix sandbox builds enabled)
- [ ] **Built on platform(s)**: 
  - [ ] Linux
  - [ ] macOS (if you have access)
  - [ ] Windows (if applicable)
- [ ] **Tested via one or more NixOS test(s)** (if applicable)
- [ ] **Tested compilation of all pkgs that depend on this change** using `nixpkgs-review wip`
- [ ] **Tested execution of all binary files** (if any)
- [ ] **Meets Nixpkgs contribution standards**

**PR Description**:
```markdown
## Description

This PR adds `langgraph-runtime-inmem-open`, an open-source alternative to the closed-source `langgraph-runtime-inmem` package. This solves critical supply-chain security issues for Nixpkgs users.

## Problem Solved

The original `langgraph-runtime-inmem` package is:
- ❌ Closed-source (no public repository)
- ❌ PyPI-only (supply-chain security risk)
- ❌ Not auditable (cannot verify security)
- ❌ Blocks Nixpkgs inclusion

## Solution

This open-source alternative provides:
- ✅ 100% open source (MIT licensed)
- ✅ GitHub hosted with full transparency
- ✅ Fully auditable code
- ✅ Same API as original package
- ✅ Drop-in replacement for `langgraph-cli[inmem]`

## Changes Made

1. **Added package definition** for `langgraph-runtime-inmem-open`
2. **Updated `langgraph-cli`** to use the open-source alternative
3. **Added comprehensive tests** and documentation

## Testing

- ✅ Package builds successfully with sandboxing enabled
- ✅ All 19 tests pass
- ✅ Python imports work correctly
- ✅ Compatible with existing LangGraph workflows
- ✅ Tested on Linux (and macOS if available)

## Related Issues

- Closes: https://github.com/NixOS/nixpkgs/issues/430234
- Addresses: https://github.com/langchain-ai/langgraph/issues/5802

## Maintainer Information

- **Author**: Abdulmalik Alquwayfili (af.alquwayfili@gmail.com)
- **Repository**: https://github.com/AbdulmalikDS/langgraph-runtime-inmem-open
- **License**: MIT
```

## 🎯 **Next Steps After PR (Following Official Guidelines)**

### **Getting Your PR Reviewed and Merged**

**Important**: PRs can take time to be reviewed. This is normal for Nixpkgs.

1. **Wait for review** - Committers are volunteers and may take days/weeks
2. **Respond to feedback** - Address all review comments promptly
3. **Keep PR in mergeable state** - Always ensure it can be merged
4. **Be patient and polite** - Remember committers work unpaid in their free time

### **If Your PR Gets Stuck**

**After 1 week of no activity**:

1. **Post in NixOS Discourse**: Look for "PRs ready for review" threads
2. **Join Matrix**: Use the Nixpkgs Review Requests room
3. **Ask nicely**: @-mention potential reviewers
4. **Get community help**: Ask others to review your PR

### **Handling Review Feedback**

- **Address all comments** - Even if they seem minor
- **Explain your reasoning** - Help reviewers understand your approach
- **Make requested changes** - Unless they're clearly optional
- **Ask for clarification** - If you don't understand a request

### **Getting Help**

**Official Resources**:
- **Nixpkgs Documentation**: https://nixos.org/manual/nixpkgs/
- **Python Packaging Guide**: https://nixos.org/manual/nixpkgs/#python
- **GitHub Issues**: https://github.com/NixOS/nixpkgs/issues
- **NixOS Discourse**: https://discourse.nixos.org/
- **Matrix Channels**: #nixpkgs:matrix.org

### **Success Metrics**

Your PR will be successful when:
- ✅ Package builds without errors (with sandboxing)
- ✅ All tests pass
- ✅ `langgraph-cli` works with your package
- ✅ PR is approved by at least one committer
- ✅ PR is merged into master
- ✅ Nixpkgs users can now use the secure alternative

### **After Merge**

Once merged, your contribution will:
1. **Flow to Hydra** - Automated builds and testing
2. **Appear in channels** - Eventually in nixpkgs-unstable
3. **Be available to users** - Via `nix-env` or `nix-shell`
4. **Help the community** - Solve the supply-chain security issue

---

**🎉 Congratulations! You're making a significant contribution to the Nixpkgs community!**

**Remember**: The goal is to solve the supply-chain security issue and provide a transparent, auditable alternative to the closed-source package. Your work will benefit the entire Nixpkgs ecosystem. 
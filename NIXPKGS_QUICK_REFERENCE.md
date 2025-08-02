# 🚀 Nixpkgs Contribution Quick Reference

## **Essential Commands**

### **Setup**
```bash
# Fork nixpkgs on GitHub first, then:
git clone https://github.com/YOUR_USERNAME/nixpkgs.git
cd nixpkgs
git remote add upstream https://github.com/NixOS/nixpkgs.git
git fetch upstream
git switch --create add-langgraph-runtime-inmem-open upstream/master
```

### **Testing (Required)**
```bash
# Enable sandboxing in /etc/nix/nix.conf:
# sandbox = true

# Test your package
nix-build -A python3Packages.langgraph-runtime-inmem-open

# Test dependent packages
nix-shell -p nixpkgs-review --run "nixpkgs-review wip"

# Format Nix files
nix fmt
```

### **Commit & Push**
```bash
git add .
git commit -m "python3Packages.langgraph-runtime-inmem-open: init at 0.1.0

Add open-source alternative to langgraph-runtime-inmem package.
This solves supply-chain security issues for Nixpkgs users.

Closes: https://github.com/NixOS/nixpkgs/issues/430234"

git push --set-upstream origin HEAD
```

## **Key Files to Create/Modify**

1. **`pkgs/development/python-modules/langgraph-runtime-inmem-open.nix`** - Package definition
2. **`pkgs/top-level/python-packages.nix`** - Add package to list
3. **Update `langgraph-cli` package** - Replace closed-source dependency

## **PR Checklist**

- [ ] **Tested using sandboxing** (required)
- [ ] **Built on platform(s)**: Linux (required), macOS (if available)
- [ ] **Tested compilation of dependent packages** using `nixpkgs-review wip`
- [ ] **Tested execution of binary files** (if any)
- [ ] **Meets Nixpkgs contribution standards**

## **Getting Help**

- **Stuck for 1+ week?** Post in NixOS Discourse "PRs ready for review"
- **Need help?** Join Matrix: #nixpkgs:matrix.org
- **Documentation**: https://nixos.org/manual/nixpkgs/

## **Remember**

- **Be patient** - PRs can take weeks to review
- **Be polite** - Committers are unpaid volunteers
- **Follow standards** - Adhere to Nixpkgs conventions
- **Test thoroughly** - Sandboxing is mandatory

---

**Goal**: Solve supply-chain security by providing open-source alternative to `langgraph-runtime-inmem` 
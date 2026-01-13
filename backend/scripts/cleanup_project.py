"""
Family CFO - Project Cleanup Script
Automated code sanitization for Docker deployment
"""
import os
import shutil
import glob

def create_dir(path):
    """Create directory if it doesn't exist"""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"📁 创建目录: {path}")
    else:
        print(f"✓ 目录已存在: {path}")

def move_files(pattern, dest):
    """Move files matching pattern to destination"""
    files = glob.glob(pattern)
    if not files:
        print(f"ℹ️ 未找到匹配文件: {pattern}")
        return
    
    for f in files:
        try:
            filename = os.path.basename(f)
            dest_path = os.path.join(dest, filename)
            if os.path.exists(dest_path):
                print(f"⏭️ 跳过 (已存在): {f}")
            else:
                shutil.move(f, dest)
                print(f"🚚 移动: {f} -> {dest}")
        except Exception as e:
            print(f"⚠️ 移动失败 {f}: {e}")

def remove_items(patterns):
    """Remove files/directories matching patterns"""
    for pattern in patterns:
        items = glob.glob(pattern, recursive=True)
        if not items:
            continue
            
        for item in items:
            try:
                if os.path.isdir(item):
                    shutil.rmtree(item)
                    print(f"🗑️ 删除文件夹: {item}")
                else:
                    os.remove(item)
                    print(f"🗑️ 删除文件: {item}")
            except Exception as e:
                print(f"⚠️ 删除失败 {item}: {e}")

def main():
    print("=" * 60)
    print("🧹 Family CFO 项目大扫除")
    print("=" * 60)
    print()

    # 1. 归档文档
    print("📚 Phase 1: 归档文档...")
    create_dir("docs")
    
    # Move all .md files except README.md
    md_files = glob.glob("*.md")
    for md_file in md_files:
        if md_file.lower() != "readme.md":
            try:
                shutil.move(md_file, "docs/")
                print(f"🚚 移动: {md_file} -> docs/")
            except Exception as e:
                print(f"⚠️ 移动失败 {md_file}: {e}")
    
    print()

    # 2. 整理后端脚本
    print("🔧 Phase 2: 整理后端脚本...")
    create_dir("backend/scripts")
    
    # Move seed and mock data scripts
    backend_scripts = [
        "backend/seed.py",
        "backend/generate_mock_data.py",
        "backend/generate_via_api.py",
        "backend/test_db.py"
    ]
    
    for script in backend_scripts:
        if os.path.exists(script):
            try:
                shutil.move(script, "backend/scripts/")
                print(f"🚚 移动: {script} -> backend/scripts/")
            except Exception as e:
                print(f"⚠️ 移动失败 {script}: {e}")
    
    print()

    # 3. 删除垃圾文件和缓存
    print("🗑️ Phase 3: 删除垃圾文件...")
    trash_patterns = [
        "**/__pycache__",
        "**/*.pyc",
        "**/.DS_Store",
        "backend/test_*.py",
        "backend/tests/",
        "frontend/src/**/mock*",
        "frontend/src/data/mockData.ts",
        "admin/src/**/mock*",
        "admin/src/data/mockData.ts",
        "**/*.log",
        "*.bat",
        "*.ps1"
    ]
    
    remove_items(trash_patterns)
    
    print()

    # 4. 清理 node_modules 缓存 (可选)
    print("📦 Phase 4: 清理构建缓存...")
    cache_patterns = [
        "frontend/node_modules/.vite",
        "admin/node_modules/.vite",
        "frontend/dist",
        "admin/dist"
    ]
    
    remove_items(cache_patterns)
    
    print()

    print("=" * 60)
    print("✨ 清理完成!")
    print("=" * 60)
    print()
    print("📋 下一步:")
    print("1. 检查 backend/scripts/ 确保脚本路径引用正确")
    print("2. 在 VS Code 搜索并删除所有 console.log")
    print("3. 检查 .gitignore 包含: .env, venv/, node_modules/, __pycache__/")
    print("4. Git 提交: git commit -m 'chore: Project cleanup for production'")
    print()
    print("🐳 准备好进行 Docker 封装了!")

if __name__ == "__main__":
    main()

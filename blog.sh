#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
POSTS_DIR="$SCRIPT_DIR/posts"
BLOG_GENERATOR="$SCRIPT_DIR/blog_generator.py"

function show_help() {
    echo "Blog Helper Script for 9lbw.github.io"
    echo ""
    echo "Usage:"
    echo "  $0 new <post-name>     Create a new blog post template"
    echo "  $0 build <post-file>   Build a specific post"
    echo "  $0 rebuild             Rebuild all posts"
    echo "  $0 list                List all posts"
    echo ""
    echo "Examples:"
    echo "  $0 new my-awesome-post"
    echo "  $0 build my-awesome-post.md"
    echo "  $0 rebuild"
}

function create_new_post() {
    local post_name="$1"
    if [[ -z "$post_name" ]]; then
        echo "Error: Post name is required"
        echo "Usage: $0 new <post-name>"
        exit 1
    fi
    
    # Convert spaces to hyphens and make lowercase
    post_name=$(echo "$post_name" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')
    local post_file="$POSTS_DIR/${post_name}.md"
    
    if [[ -f "$post_file" ]]; then
        echo "Error: Post '$post_file' already exists"
        exit 1
    fi
    
    # Get current date
    local current_date=$(date +%Y-%m-%d)
    
    # Create the post template
    cat > "$post_file" << EOF
---
title: "Your Post Title Here"
date: "$current_date"
description: "A brief description of your post for the blog listing"
---

# Your Post Title Here

Write your blog post content here using Markdown syntax.

## Subheading Example

You can use:
- **Bold text**
- *Italic text*
- \`inline code\`
- [Links](https://example.com)

### Code Blocks

\`\`\`python
def hello_world():
    print("Hello, World!")
\`\`\`

### Math (with KaTeX)

You can include math equations:
- Inline: \$E = mc^2\$
- Display: \$\$\\sum_{i=1}^{n} x_i = x_1 + x_2 + \\ldots + x_n\$\$

Happy writing!
EOF
    
    echo "Created new post: $post_file"
    echo "Edit the file, then run: $0 build ${post_name}.md"
}

function build_post() {
    local post_file="$1"
    if [[ -z "$post_file" ]]; then
        echo "Error: Post file is required"
        echo "Usage: $0 build <post-file>"
        exit 1
    fi
    
    # Add .md extension if not present
    if [[ "$post_file" != *.md ]]; then
        post_file="${post_file}.md"
    fi
    
    # Check if file exists in posts directory
    if [[ ! -f "$POSTS_DIR/$post_file" ]]; then
        echo "Error: Post file '$POSTS_DIR/$post_file' not found"
        exit 1
    fi
    
    echo "Building post: $post_file"
    python "$BLOG_GENERATOR" "$POSTS_DIR/$post_file"
}

function rebuild_all() {
    echo "Rebuilding all posts..."
    python "$BLOG_GENERATOR" --rebuild-all
}

function list_posts() {
    echo "Available posts:"
    if [[ -d "$POSTS_DIR" ]]; then
        find "$POSTS_DIR" -name "*.md" -printf "%f\n" | sort
    else
        echo "No posts directory found"
    fi
}

# Main script logic
case "${1:-}" in
    "new")
        create_new_post "$2"
        ;;
    "build")
        build_post "$2"
        ;;
    "rebuild")
        rebuild_all
        ;;
    "list")
        list_posts
        ;;
    "help"|"-h"|"--help"|"")
        show_help
        ;;
    *)
        echo "Error: Unknown command '$1'"
        echo ""
        show_help
        exit 1
        ;;
esac

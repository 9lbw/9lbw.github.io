#!/usr/bin/env python3
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import markdown
    from markdown.extensions import codehilite, toc, tables, fenced_code
except ImportError:
    print("Error: markdown package not found. Install it with: pip install markdown")
    sys.exit(1)

try:
    import frontmatter
except ImportError:
    print("Error: python-frontmatter package not found. Install it with: pip install python-frontmatter")
    sys.exit(1)


class BlogPost:
    def __init__(self, title: str, date: str, description: str, content: str, filename: str):
        self.title = title
        self.date = date
        self.description = description
        self.content = content
        self.filename = filename
        self.html_filename = filename.replace('.md', '.html')
        
    @property
    def url(self) -> str:
        return f"blog/{self.html_filename}"
        
    def __repr__(self):
        return f"BlogPost(title='{self.title}', date='{self.date}', filename='{self.filename}')"


class BlogGenerator:
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.blog_dir = self.root_dir / "blog"
        self.posts_dir = self.root_dir / "posts"  # Where markdown files are stored
        self.index_file = self.root_dir / "index.html"
        
        # Create directories if they don't exist
        self.blog_dir.mkdir(exist_ok=True)
        self.posts_dir.mkdir(exist_ok=True)
        
        # Configure markdown processor
        self.md = markdown.Markdown(
            extensions=[
                'codehilite',
                'toc',
                'tables',
                'fenced_code',
                'markdown.extensions.extra'
            ],
            extension_configs={
                'codehilite': {
                    'css_class': 'highlight',
                    'use_pygments': False  # Use highlight.js instead
                }
            }
        )
    
    def parse_markdown_file(self, filepath: Path) -> BlogPost:
        """Parse a markdown file with frontmatter and return a BlogPost object."""
        with open(filepath, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        # Extract metadata
        title = post.metadata.get('title', filepath.stem.replace('-', ' ').title())
        date = post.metadata.get('date', datetime.now().strftime('%Y-%m-%d'))
        description = post.metadata.get('description', '')
        
        # Convert markdown content to HTML
        html_content = self.md.convert(post.content)
        
        return BlogPost(
            title=title,
            date=date,
            description=description,
            content=html_content,
            filename=filepath.name
        )
    
    def generate_html_template(self, post: BlogPost) -> str:
        """Generate the complete HTML file for a blog post."""
        template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{post.title} - 9lbw</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
    <link rel="stylesheet" href="../styles.css">
    <!-- Highlight.js theme -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/github-dark.min.css">
</head>
<body class="light-mode">
    <div class="container">
        <header class="header">
            <h1 class="name"><a href="../index.html">9lbw</a></h1>
            <p class="tagline">Self-proclaimed Software Engineer</p>
        </header>

        <nav class="navigation">
            <a href="../index.html#about">About</a>
            <a href="../index.html#projects">Projects</a>
            <a href="../index.html#blog">Blog</a>
            <button id="theme-toggle" class="theme-toggle">◐</button>
        </nav>

        <main class="content">
            <article class="blog-post-full">
                <h1>{post.title}</h1>
                <time>{self.format_date(post.date)}</time>
                
                <div class="blog-content">
                    {post.content}
                </div>

                <div class="blog-navigation">
                    <a href="../index.html#blog" class="back-link">← Back to Blog</a>
                </div>
            </article>
        </main>

        <footer class="footer">
            <p>© 2025 9lbw.</p>
            <div class="contact">
                <a href="https://github.com/9lbw">GitHub</a>
                <a href="mailto:contact@9lbw.dev">Email</a>
            </div>
        </footer>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js"></script>
    <!-- Highlight.js -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/highlight.min.js"></script>
    <script>hljs.highlightAll();</script>
    <script>
        document.addEventListener("DOMContentLoaded", function() {{
            renderMathInElement(document.body, {{
                delimiters: [
                    {{left: "$$", right: "$$", display: true}},
                    {{left: "$", right: "$", display: false}}
                ]
            }});

            // Dark mode toggle functionality
            const themeToggle = document.getElementById('theme-toggle');
            const body = document.body;
            
            // Check for saved theme preference or default to light mode
            const savedTheme = localStorage.getItem('theme') || 'light';
            body.classList.add(savedTheme + '-mode');
            
            themeToggle.addEventListener('click', () => {{
                if (body.classList.contains('light-mode')) {{
                    body.classList.remove('light-mode');
                    body.classList.add('dark-mode');
                    localStorage.setItem('theme', 'dark');
                }} else {{
                    body.classList.remove('dark-mode');
                    body.classList.add('light-mode');
                    localStorage.setItem('theme', 'light');
                }}
            }});
        }});
    </script>
</body>
</html>'''
        return template
    
    def format_date(self, date_str: str) -> str:
        """Format date string to a readable format."""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.strftime('%B %d, %Y')
        except ValueError:
            return date_str
    
    def get_all_posts(self) -> List[BlogPost]:
        """Get all blog posts from markdown files, sorted by date (newest first)."""
        posts = []
        
        # Look for markdown files in the posts directory
        for md_file in self.posts_dir.glob('*.md'):
            try:
                post = self.parse_markdown_file(md_file)
                posts.append(post)
            except Exception as e:
                print(f"Error parsing {md_file}: {e}")
        
        # Sort by date (newest first)
        posts.sort(key=lambda p: p.date, reverse=True)
        return posts
    
    def generate_blog_post(self, markdown_file: Path) -> BlogPost:
        """Generate HTML blog post from markdown file."""
        print(f"Processing {markdown_file}...")
        
        # Parse the markdown file
        post = self.parse_markdown_file(markdown_file)
        
        # Generate HTML content
        html_content = self.generate_html_template(post)
        
        # Write HTML file
        output_file = self.blog_dir / post.html_filename
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Generated {output_file}")
        return post
    
    def update_index_html(self, posts: List[BlogPost]):
        """Update the index.html file with the latest blog posts."""
        if not self.index_file.exists():
            print(f"Error: {self.index_file} not found")
            return
        
        with open(self.index_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Generate blog section HTML
        blog_articles = []
        for post in posts:
            article_html = f'''                <article class="blog-post">
                    <h3><a href="{post.url}">{post.title}</a></h3>
                    <time>{self.format_date(post.date)}</time>
                    <p>{post.description}</p>
                </article>'''
            blog_articles.append(article_html)
        
        blog_section_html = '''            <section id="blog" class="section">
                <h2>Blog</h2>
''' + '\\n'.join(blog_articles) + '''
            </section>'''
        
        # Replace the blog section
        pattern = r'<section id="blog" class="section">.*?</section>'
        new_content = re.sub(pattern, blog_section_html, content, flags=re.DOTALL)
        
        # Write updated content back
        with open(self.index_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"Updated {self.index_file} with {len(posts)} blog posts")
    
    def rebuild_all(self):
        """Rebuild all blog posts and update index."""
        print("Rebuilding all blog posts...")
        posts = []
        
        for md_file in self.posts_dir.glob('*.md'):
            try:
                post = self.generate_blog_post(md_file)
                posts.append(post)
            except Exception as e:
                print(f"Error processing {md_file}: {e}")
        
        # Update index with all posts
        if posts:
            posts.sort(key=lambda p: p.date, reverse=True)
            self.update_index_html(posts)
        
        print(f"Rebuilt {len(posts)} blog posts")
    
    def process_single_file(self, markdown_file: str):
        """Process a single markdown file and update the index."""
        md_path = Path(markdown_file)
        
        if not md_path.exists():
            # Try looking in the posts directory
            md_path = self.posts_dir / markdown_file
            if not md_path.exists():
                print(f"Error: File {markdown_file} not found")
                return
        
        # Generate the blog post
        new_post = self.generate_blog_post(md_path)
        
        # Get all posts and update index
        all_posts = self.get_all_posts()
        self.update_index_html(all_posts)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\\nExamples:")
        print("  python blog_generator.py posts/my-new-post.md")
        print("  python blog_generator.py --rebuild-all")
        sys.exit(1)
    
    generator = BlogGenerator()
    
    if sys.argv[1] == "--rebuild-all":
        generator.rebuild_all()
    else:
        generator.process_single_file(sys.argv[1])


if __name__ == "__main__":
    main()

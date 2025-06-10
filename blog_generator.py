#!/usr/bin/env python3
"""
Blog Generator - Efficiently manage blog posts for static site generation.

This tool generates HTML blog posts from markdown files and maintains
an up-to-date index.html with incremental updates instead of replacing
the entire blog section each time.

Usage:
    python blog_generator.py <markdown_file>     # Process single file
    python blog_generator.py --rebuild-all       # Rebuild everything
    python blog_generator.py --verify           # Check blog integrity
    python blog_generator.py --status           # Show blog status
"""
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

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: beautifulsoup4 package not found. Install it with: pip install beautifulsoup4")
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
    
    def get_existing_blog_posts_from_html(self) -> Dict[str, Dict]:
        """Parse existing blog posts from index.html to avoid duplicates."""
        if not self.index_file.exists():
            return {}
        
        with open(self.index_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        blog_section = soup.find('section', id='blog')
        existing_posts = {}
        
        if blog_section:
            articles = blog_section.find_all('article', class_='blog-post')
            for article in articles:
                link = article.find('a')
                time_elem = article.find('time')
                desc_elem = article.find('p')
                
                if link and link.get('href'):
                    url = link.get('href')
                    filename = Path(url).name
                    existing_posts[filename] = {
                        'element': article,
                        'url': url,
                        'title': link.get_text(strip=True),
                        'date': time_elem.get_text(strip=True) if time_elem else '',
                        'description': desc_elem.get_text(strip=True) if desc_elem else ''
                    }
        
        return existing_posts

    def add_or_update_blog_post(self, post: BlogPost):
        """Add a new blog post or update an existing one in index.html."""
        if not self.index_file.exists():
            print(f"Error: {self.index_file} not found")
            return
        
        with open(self.index_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        blog_section = soup.find('section', id='blog')
        
        if not blog_section:
            print("Error: Blog section not found in index.html")
            return
        
        existing_posts = self.get_existing_blog_posts_from_html()
        
        # Create new article element
        new_article = soup.new_tag('article', **{'class': 'blog-post'})
        
        h3 = soup.new_tag('h3')
        link = soup.new_tag('a', href=post.url)
        link.string = post.title
        h3.append(link)
        new_article.append(h3)
        
        time_elem = soup.new_tag('time')
        time_elem.string = self.format_date(post.date)
        new_article.append(time_elem)
        
        if post.description:
            p = soup.new_tag('p')
            p.string = post.description
            new_article.append(p)
        
        # Check if post already exists
        if post.html_filename in existing_posts:
            # Update existing post in place
            old_article = existing_posts[post.html_filename]['element']
            old_article.replace_with(new_article)
            print(f"Updated existing blog post: {post.title}")
        else:
            # Add new post in chronological order (newest first)
            articles = blog_section.find_all('article', class_='blog-post')
            inserted = False
            
            try:
                new_date_obj = datetime.strptime(post.date, '%Y-%m-%d')
                
                for article in articles:
                    time_elem = article.find('time')
                    if time_elem:
                        existing_date = time_elem.get_text(strip=True)
                        try:
                            existing_date_obj = datetime.strptime(self.parse_display_date(existing_date), '%Y-%m-%d')
                            
                            if new_date_obj > existing_date_obj:
                                article.insert_before(new_article)
                                inserted = True
                                break
                        except ValueError:
                            # If date parsing fails, skip this article
                            continue
                
                # If not inserted yet, add after the h2 header or at the end
                if not inserted:
                    # Find the h2 element and insert after it
                    h2 = blog_section.find('h2')
                    if h2 and h2.next_sibling:
                        h2.insert_after(new_article)
                    else:
                        blog_section.append(new_article)
                
                print(f"Added new blog post: {post.title}")
                
            except ValueError as e:
                print(f"Error parsing date for post {post.title}: {e}")
                # Fallback: add at the end
                blog_section.append(new_article)
                print(f"Added blog post at end due to date parsing error: {post.title}")
        
        # Write back to file with proper formatting
        with open(self.index_file, 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify()))

    def parse_display_date(self, display_date: str) -> str:
        """Convert display date back to YYYY-MM-DD format."""
        try:
            # Try to parse "Month DD, YYYY" format
            date_obj = datetime.strptime(display_date, '%B %d, %Y')
            return date_obj.strftime('%Y-%m-%d')
        except ValueError:
            # If parsing fails, assume it's already in the right format
            return display_date
    
    def rebuild_blog_section(self, posts: List[BlogPost]):
        """Completely rebuild the blog section (fallback method only for --rebuild-all)."""
        if not self.index_file.exists():
            print(f"Error: {self.index_file} not found")
            return
        
        with open(self.index_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        blog_section = soup.find('section', id='blog')
        
        if not blog_section:
            print("Error: Blog section not found in index.html")
            return
        
        # Clear existing blog posts but keep the h2 header
        h2 = blog_section.find('h2')
        blog_section.clear()
        if h2:
            blog_section.append(h2)
        
        # Add all posts in order
        for post in posts:
            article = soup.new_tag('article', **{'class': 'blog-post'})
            
            h3 = soup.new_tag('h3')
            link = soup.new_tag('a', href=post.url)
            link.string = post.title
            h3.append(link)
            article.append(h3)
            
            time_elem = soup.new_tag('time')
            time_elem.string = self.format_date(post.date)
            article.append(time_elem)
            
            if post.description:
                p = soup.new_tag('p')
                p.string = post.description
                article.append(p)
            
            blog_section.append(article)
        
        # Write updated content back
        with open(self.index_file, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        
        print(f"Rebuilt blog section with {len(posts)} blog posts")
    
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
        
        # Update index with all posts using complete rebuild
        if posts:
            posts.sort(key=lambda p: p.date, reverse=True)
            self.rebuild_blog_section(posts)
        
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
        
        # Add or update this specific post in index.html
        self.add_or_update_blog_post(new_post)

    def verify_blog_integrity(self) -> bool:
        """Verify that all markdown files have corresponding HTML files and index entries."""
        if not self.index_file.exists():
            print("Warning: index.html not found")
            return False
        
        # Get markdown files
        md_files = {f.stem: f for f in self.posts_dir.glob('*.md')}
        
        # Get HTML files
        html_files = {f.stem: f for f in self.blog_dir.glob('*.html')}
        
        # Get index entries
        existing_posts = self.get_existing_blog_posts_from_html()
        index_entries = {Path(p['url']).stem: p for p in existing_posts.values()}
        
        all_good = True
        
        # Check for missing HTML files
        for md_name in md_files:
            if md_name not in html_files:
                print(f"Missing HTML file for: {md_name}.md")
                all_good = False
        
        # Check for missing index entries
        for md_name in md_files:
            if md_name not in index_entries:
                print(f"Missing index entry for: {md_name}.md")
                all_good = False
        
        # Check for orphaned HTML files
        for html_name in html_files:
            if html_name not in md_files:
                print(f"Orphaned HTML file (no markdown source): {html_name}.html")
        
        # Check for orphaned index entries
        for index_name in index_entries:
            if index_name not in md_files:
                print(f"Orphaned index entry (no markdown source): {index_name}")
        
        if all_good:
            print(f"Blog integrity check passed: {len(md_files)} posts verified")
        
        return all_good
    
    def get_blog_status(self):
        """Print current blog status."""
        md_count = len(list(self.posts_dir.glob('*.md')))
        html_count = len(list(self.blog_dir.glob('*.html')))
        index_entries = len(self.get_existing_blog_posts_from_html())
        
        print(f"Blog Status:")
        print(f"  Markdown files: {md_count}")
        print(f"  HTML files: {html_count}")
        print(f"  Index entries: {index_entries}")
        
        if md_count != html_count or md_count != index_entries:
            print("  ⚠️  Inconsistency detected - consider running --rebuild-all")
        else:
            print("  ✅ All files in sync")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nExamples:")
        print("  python blog_generator.py posts/my-new-post.md")
        print("  python blog_generator.py --rebuild-all")
        print("  python blog_generator.py --verify")
        print("  python blog_generator.py --status")
        sys.exit(1)
    
    generator = BlogGenerator()
    
    if sys.argv[1] == "--rebuild-all":
        generator.rebuild_all()
    elif sys.argv[1] == "--verify":
        generator.verify_blog_integrity()
    elif sys.argv[1] == "--status":
        generator.get_blog_status()
    else:
        generator.process_single_file(sys.argv[1])


if __name__ == "__main__":
    main()

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path
import os

app = FastAPI(
    title="Polar Bear Conservation Website",
    description="A promotional website to raise awareness about polar bear conservation",
    version="1.0.0"
)

# Mount static files from the frontend directory
frontend_path = Path(__file__).parent.parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main polar bear conservation webpage"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Protect Polar Bears - Conservation Awareness</title>
        <link rel="stylesheet" href="/static/styles.css">
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&family=Open+Sans:wght@400;600&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    </head>
    <body>
        <header class="header">
            <div class="container">
                <nav class="navbar">
                    <div class="logo">
                        <i class="fas fa-paw"></i>
                        <span>Protect Polar Bears</span>
                    </div>
                    <ul class="nav-links">
                        <li><a href="#home">Home</a></li>
                        <li><a href="#threats">Threats</a></li>
                        <li><a href="#solutions">Solutions</a></li>
                        <li><a href="#take-action">Take Action</a></li>
                        <li><a href="#about">About</a></li>
                    </ul>
                    <button class="donate-btn">Donate Now</button>
                </nav>
            </div>
        </header>

        <main>
            <section id="home" class="hero">
                <div class="container">
                    <div class="hero-content">
                        <h1>Save Our Polar Bears</h1>
                        <p class="hero-subtitle">Climate change is melting their home. Join the fight to protect these majestic Arctic giants before it's too late.</p>
                        <div class="hero-actions">
                            <a href="#take-action" class="btn-primary">Take Action</a>
                            <a href="#learn-more" class="btn-secondary">Learn More</a>
                        </div>
                    </div>
                </div>
            </section>

            <section id="threats" class="threats-section">
                <div class="container">
                    <h2>Major Threats to Polar Bears</h2>
                    <div class="threats-grid">
                        <div class="threat-card">
                            <div class="threat-icon">
                                <i class="fas fa-temperature-high"></i>
                            </div>
                            <h3>Climate Change</h3>
                            <p>Arctic sea ice is melting at an alarming rate, reducing polar bear hunting grounds and access to food.</p>
                        </div>
                        <div class="threat-card">
                            <div class="threat-icon">
                                <i class="fas fa-industry"></i>
                            </div>
                            <h3>Pollution</h3>
                            <p>Toxic chemicals accumulate in the Arctic food chain, affecting polar bear health and reproduction.</p>
                        </div>
                        <div class="threat-card">
                            <div class="threat-icon">
                                <i class="fas fa-oil-can"></i>
                            </div>
                            <h3>Oil Exploration</h3>
                            <p>Increased industrial activity in the Arctic threatens polar bear habitats with oil spills and disruption.</p>
                        </div>
                        <div class="threat-card">
                            <div class="threat-icon">
                                <i class="fas fa-fish"></i>
                            </div>
                            <h3>Food Scarcity</h3>
                            <p>Declining seal populations due to changing ice conditions leave polar bears struggling to find enough food.</p>
                        </div>
                    </div>
                </div>
            </section>

            <section id="solutions" class="solutions-section">
                <div class="container">
                    <h2>How We Can Help</h2>
                    <div class="solutions-content">
                        <div class="solution-item">
                            <h3><i class="fas fa-leaf"></i> Reduce Carbon Footprint</h3>
                            <p>Support renewable energy, use public transportation, and reduce energy consumption to combat climate change.</p>
                        </div>
                        <div class="solution-item">
                            <h3><i class="fas fa-hands-helping"></i> Support Conservation</h3>
                            <p>Donate to organizations working to protect polar bear habitats and conduct vital research.</p>
                        </div>
                        <div class="solution-item">
                            <h3><i class="fas fa-bullhorn"></i> Raise Awareness</h3>
                            <p>Share information about polar bear conservation with friends, family, and on social media.</p>
                        </div>
                        <div class="solution-item">
                            <h3><i class="fas fa-vote-yea"></i> Advocate for Policy</h3>
                            <p>Support legislation that protects Arctic ecosystems and reduces greenhouse gas emissions.</p>
                        </div>
                    </div>
                </div>
            </section>

            <section id="take-action" class="action-section">
                <div class="container">
                    <h2>Take Action Today</h2>
                    <p class="section-subtitle">Every action counts in the fight to save polar bears from extinction.</p>
                    
                    <div class="action-cards">
                        <div class="action-card">
                            <div class="action-icon">
                                <i class="fas fa-donate"></i>
                            </div>
                            <h3>Make a Donation</h3>
                            <p>Your contribution funds critical conservation efforts and research.</p>
                            <button class="action-btn">Donate Now</button>
                        </div>
                        
                        <div class="action-card">
                            <div class="action-icon">
                                <i class="fas fa-envelope"></i>
                            </div>
                            <h3>Sign Petitions</h3>
                            <p>Join thousands in urging governments to protect Arctic habitats.</p>
                            <button class="action-btn">Sign Petition</button>
                        </div>
                        
                        <div class="action-card">
                            <div class="action-icon">
                                <i class="fas fa-users"></i>
                            </div>
                            <h3>Volunteer</h3>
                            <p>Join local conservation groups and participate in awareness campaigns.</p>
                            <button class="action-btn">Get Involved</button>
                        </div>
                    </div>
                    
                    <div class="newsletter">
                        <h3>Stay Informed</h3>
                        <p>Subscribe to our newsletter for updates on polar bear conservation efforts.</p>
                        <form class="newsletter-form">
                            <input type="email" placeholder="Enter your email address" required>
                            <button type="submit">Subscribe</button>
                        </form>
                    </div>
                </div>
            </section>
        </main>

        <footer class="footer">
            <div class="container">
                <div class="footer-content">
                    <div class="footer-section">
                        <h3>Protect Polar Bears</h3>
                        <p>Dedicated to the conservation and protection of polar bears and their Arctic habitat.</p>
                        <div class="social-links">
                            <a href="#"><i class="fab fa-facebook"></i></a>
                            <a href="#"><i class="fab fa-twitter"></i></a>
                            <a href="#"><i class="fab fa-instagram"></i></a>
                            <a href="#"><i class="fab fa-youtube"></i></a>
                        </div>
                    </div>
                    
                    <div class="footer-section">
                        <h4>Quick Links</h4>
                        <ul>
                            <li><a href="#home">Home</a></li>
                            <li><a href="#threats">Threats</a></li>
                            <li><a href="#solutions">Solutions</a></li>
                            <li><a href="#take-action">Take Action</a></li>
                        </ul>
                    </div>
                    
                    <div class="footer-section">
                        <h4>Resources</h4>
                        <ul>
                            <li><a href="#">Research Papers</a></li>
                            <li><a href="#">Educational Materials</a></li>
                            <li><a href="#">Conservation Partners</a></li>
                            <li><a href="#">Annual Reports</a></li>
                        </ul>
                    </div>
                    
                    <div class="footer-section">
                        <h4>Contact Us</h4>
                        <p><i class="fas fa-envelope"></i> info@protectpolarbears.org</p>
                        <p><i class="fas fa-phone"></i> +1 (555) 123-4567</p>
                        <p><i class="fas fa-map-marker-alt"></i> Arctic Conservation Center</p>
                    </div>
                </div>
                
                <div class="footer-bottom">
                    <p>&copy; 2024 Protect Polar Bears. All rights reserved. | <a href="#">Privacy Policy</a> | <a href="#">Terms of Service</a></p>
                </div>
            </div>
        </footer>

        <script>
            // Simple JavaScript for newsletter form submission
            document.querySelector('.newsletter-form').addEventListener('submit', function(e) {
                e.preventDefault();
                const email = this.querySelector('input[type="email"]').value;
                alert(`Thank you for subscribing with ${email}! You'll receive updates on polar bear conservation.`);
                this.reset();
            });
            
            // Smooth scrolling for navigation links
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                anchor.addEventListener('click', function(e) {
                    e.preventDefault();
                    const targetId = this.getAttribute('href');
                    if(targetId === '#') return;
                    
                    const targetElement = document.querySelector(targetId);
                    if(targetElement) {
                        window.scrollTo({
                            top: targetElement.offsetTop - 80,
                            behavior: 'smooth'
                        });
                    }
                });
            });
            
            // Donation button alert
            document.querySelectorAll('.donate-btn, .action-btn').forEach(btn => {
                btn.addEventListener('click', function() {
                    alert('Thank you for your interest in supporting polar bear conservation! You would be redirected to our secure donation portal.');
                });
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "service": "polar-bear-conservation", "version": "1.0.0"}

@app.get("/api/info")
async def get_site_info():
    """API endpoint for site information"""
    return {
        "site_name": "Protect Polar Bears",
        "description": "Promotional website for polar bear conservation awareness",
        "features": [
            "Educational content about polar bear threats",
            "Conservation solutions and actions",
            "Responsive design for all devices",
            "Interactive elements for engagement"
        ],
        "contact": {
            "email": "info@protectpolarbears.org",
            "organization": "Arctic Conservation Center"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

import FeatureExperience from '@/components/FeatureExperience';
import './globals.css';

export default function Home() {
  return (
    <div className="page-container">
      <header className="main-header">
        <div className="header-content">
          <h1 className="site-title">Wuhan Specialty Snacks</h1>
          <p className="site-tagline">A Culinary Journey Through the Streets of Wuhan</p>
          <nav className="main-nav" aria-label="Main navigation">
            <ul className="nav-list">
              <li><a href="#snack-showcase" className="nav-link">Snacks</a></li>
              <li><a href="#about" className="nav-link">About</a></li>
              <li><a href="#contact" className="nav-link">Contact</a></li>
            </ul>
          </nav>
        </div>
      </header>

      <main className="main-content">
        <section className="intro-section" id="about">
          <div className="container">
            <h2 className="section-title">Discover Wuhan&apos;s Street Food Culture</h2>
            <p className="section-text">
              Wuhan, the capital of Hubei province, is famous for its vibrant street food scene.
              From breakfast noodles to late-night snacks, the city offers a diverse array of
              flavors that reflect its rich history and cultural diversity. This page showcases
              some of the most iconic snacks you must try when visiting Wuhan.
            </p>
          </div>
        </section>

        <FeatureExperience />

        <section className="info-section">
          <div className="container">
            <h2 className="section-title">Experience Wuhan Street Food</h2>
            <div className="info-grid">
              <div className="info-card">
                <h3 className="info-card-title">Best Time to Visit</h3>
                <p className="info-card-text">
                  Street food stalls are most vibrant in the early morning for breakfast
                  and in the evening for dinner snacks. Night markets come alive after sunset.
                </p>
              </div>
              <div className="info-card">
                <h3 className="info-card-title">Where to Find</h3>
                <p className="info-card-text">
                  Head to Hubu Alley, Jianghan Road Pedestrian Street, or any local
                  residential area for authentic Wuhan snack experiences.
                </p>
              </div>
              <div className="info-card">
                <h3 className="info-card-title">Eating Etiquette</h3>
                <p className="info-card-text">
                  Most snacks are meant to be eaten on the go. Don&apos;t be shy to eat
                  while walking—it&apos;s part of the local culture!
                </p>
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer className="main-footer" id="contact">
        <div className="container">
          <div className="footer-content">
            <div className="footer-section">
              <h3 className="footer-title">Wuhan Specialty Snacks</h3>
              <p className="footer-text">
                A static webpage showcasing the delicious street food of Wuhan, China.
                Created with HTML and CSS.
              </p>
            </div>
            <div className="footer-section">
              <h3 className="footer-title">Contact Info</h3>
              <p className="footer-text">
                For more information about Wuhan snacks, visit local tourism websites
                or contact the Wuhan Tourism Bureau.
              </p>
            </div>
            <div className="footer-section">
              <h3 className="footer-title">Attribution</h3>
              <p className="footer-text">
                This page is for educational purposes. All snack descriptions are based
                on publicly available information about Wuhan cuisine.
              </p>
            </div>
          </div>
          <div className="footer-bottom">
            <p className="copyright">&copy; {new Date().getFullYear()} Wuhan Snacks Showcase. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
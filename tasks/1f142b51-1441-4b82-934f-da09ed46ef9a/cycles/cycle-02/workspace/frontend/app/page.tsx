import Image from 'next/image';
import styles from './page.module.css';

export default function Home() {
  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1 className={styles.title}>The Adorable Red Panda</h1>
        <p className={styles.subtitle}>Discover the fascinating world of Ailurus fulgens</p>
      </header>

      <main className={styles.main}>
        <section className={styles.hero}>
          <div className={styles.heroImage}>
            <Image
              src="/images/red-panda-hero.jpg"
              alt="A red panda resting on a tree branch"
              width={800}
              height={500}
              priority
              className={styles.image}
            />
          </div>
          <div className={styles.heroContent}>
            <p>
              The red panda, also known as the lesser panda, is a small mammal native to the eastern Himalayas and southwestern China. 
              With its reddish-brown fur, bushy tail, and adorable face, it has captured hearts worldwide.
            </p>
          </div>
        </section>

        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Quick Facts</h2>
          <div className={styles.factsGrid}>
            <div className={styles.factCard}>
              <h3>Scientific Name</h3>
              <p>Ailurus fulgens</p>
            </div>
            <div className={styles.factCard}>
              <h3>Size</h3>
              <p>50-64 cm (body), 28-59 cm (tail)</p>
            </div>
            <div className={styles.factCard}>
              <h3>Weight</h3>
              <p>3-6 kg (6.6-13.2 lbs)</p>
            </div>
            <div className={styles.factCard}>
              <h3>Lifespan</h3>
              <p>8-10 years in the wild, up to 15 in captivity</p>
            </div>
          </div>
        </section>

        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Habitat & Distribution</h2>
          <div className={styles.contentRow}>
            <div className={styles.contentText}>
              <p>
                Red pandas inhabit temperate forests in the Himalayas, ranging from Nepal in the west to China in the east. 
                They are found at elevations of 2,200-4,800 meters (7,200-15,700 ft) where bamboo grows abundantly.
              </p>
              <p>
                Their habitat is characterized by cool temperatures and dense understory of bamboo. Unfortunately, 
                deforestation and habitat fragmentation have significantly reduced their range.
              </p>
            </div>
            <div className={styles.contentImage}>
              <Image
                src="/images/red-panda-habitat.jpg"
                alt="Red panda in its natural forest habitat"
                width={600}
                height={400}
                className={styles.image}
              />
            </div>
          </div>
        </section>

        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Diet & Behavior</h2>
          <div className={styles.contentRowReverse}>
            <div className={styles.contentText}>
              <p>
                Despite being classified as carnivores, red pandas primarily eat bamboo—up to 20,000 leaves per day! 
                Their diet also includes fruits, acorns, roots, eggs, and small animals when available.
              </p>
              <p>
                These solitary creatures are most active at dawn and dusk (crepuscular). They are excellent climbers 
                and spend most of their time in trees, using their semi-retractable claws and bushy tails for balance.
              </p>
            </div>
            <div className={styles.contentImage}>
              <Image
                src="/images/red-panda-eating.jpg"
                alt="Red panda eating bamboo leaves"
                width={600}
                height={400}
                className={styles.image}
              />
            </div>
          </div>
        </section>

        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Conservation Status</h2>
          <div className={styles.conservation}>
            <div className={styles.statusBadge}>
              <span className={styles.endangered}>Endangered</span>
              <p>IUCN Red List</p>
            </div>
            <div className={styles.conservationContent}>
              <p>
                Red pandas are classified as Endangered, with an estimated population of fewer than 10,000 mature individuals. 
                Their population continues to decline due to habitat loss, poaching, and inbreeding depression.
              </p>
              <p>
                Conservation efforts include protected areas, captive breeding programs, and community-based initiatives 
                to reduce human-wildlife conflict and promote sustainable livelihoods.
              </p>
              <div className={styles.cta}>
                <a 
                  href="https://www.worldwildlife.org/species/red-panda" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className={styles.ctaButton}
                >
                  Learn How to Help
                </a>
              </div>
            </div>
          </div>
        </section>

        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Fun Facts</h2>
          <div className={styles.funFacts}>
            <ul className={styles.factsList}>
              <li>Red pandas have a false thumb—an extended wrist bone that helps them grip bamboo.</li>
              <li>They communicate through twittering sounds, squeals, and body language.</li>
              <li>Their thick fur covers even the soles of their feet for insulation against cold surfaces.</li>
              <li>Red pandas are more closely related to raccoons and weasels than to giant pandas.</li>
              <li>They wrap their tails around themselves for warmth while sleeping in cold weather.</li>
            </ul>
          </div>
        </section>
      </main>

      <footer className={styles.footer}>
        <div className={styles.footerContent}>
          <p>© {new Date().getFullYear()} Red Panda Conservation Awareness</p>
          <p className={styles.disclaimer}>
            This educational website is dedicated to raising awareness about red panda conservation. 
            All images are used for educational purposes.
          </p>
          <div className={styles.footerLinks}>
            <a href="https://www.iucnredlist.org/species/714/110023718" target="_blank" rel="noopener noreferrer">
              IUCN Red List
            </a>
            <a href="https://redpandanetwork.org/" target="_blank" rel="noopener noreferrer">
              Red Panda Network
            </a>
            <a href="https://www.worldwildlife.org/species/red-panda" target="_blank" rel="noopener noreferrer">
              WWF
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
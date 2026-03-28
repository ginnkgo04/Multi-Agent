import Image from 'next/image';
import styles from './page.module.css';
import FeatureExperience from '@/components/FeatureExperience';

export default function Home() {
  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div className={styles.headerContainer}>
          <h1 className={styles.title}>Cherry Blossoms Introduction</h1>
          <nav className={styles.nav}>
            <ul className={styles.navList}>
              <li><a href="/" className={styles.navLink}>Home</a></li>
              <li><a href="/about" className={styles.navLink}>About</a></li>
              <li><a href="/contact" className={styles.navLink}>Contact</a></li>
            </ul>
          </nav>
        </div>
      </header>

      <main className={styles.main}>
        <section className={styles.hero}>
          <div className={styles.heroContent}>
            <h2 className={styles.heroTitle}>The Beauty of Sakura</h2>
            <p className={styles.heroText}>
              Cherry blossoms, known as &quot;sakura&quot; in Japan, are flowers of several trees of genus Prunus. 
              They are celebrated for their stunning beauty and cultural significance across the world.
            </p>
          </div>
          <div className={styles.heroImage}>
            <Image 
              src="/cherry-blossom.jpg" 
              alt="Beautiful pink cherry blossoms in full bloom" 
              width={800}
              height={600}
              className={styles.image}
              priority
            />
          </div>
        </section>

        <section className={styles.content}>
          <div className={styles.section}>
            <h3 className={styles.sectionTitle}>Introduction to Cherry Blossoms</h3>
            <p className={styles.sectionText}>
              Cherry blossoms are a symbolic flower of spring, a time of renewal, and the fleeting nature of life. 
              Their life is very short. After their beauty peaks around two weeks, the blossoms start to fall. 
              During this season, people enjoy hanami (flower viewing) parties under the blooming trees.
            </p>
            <p className={styles.sectionText}>
              The practice of hanami is centuries old, believed to have started during the Nara Period (710–794) 
              when it was ume (plum) blossoms that people admired. But by the Heian Period (794–1185), 
              cherry blossoms came to attract more attention.
            </p>
          </div>

          <div className={styles.section}>
            <h3 className={styles.sectionTitle}>Interesting Facts</h3>
            <ul className={styles.factsList}>
              <li className={styles.factItem}>There are over 200 varieties of cherry blossoms.</li>
              <li className={styles.factItem}>The color of cherry blossoms can range from white to deep pink.</li>
              <li className={styles.factItem}>Most cherry blossom trees don&apos;t produce fruit.</li>
              <li className={styles.factItem}>The cherry blossom is Japan&apos;s national flower.</li>
              <li className={styles.factItem}>Washington D.C.&apos;s cherry blossoms were a gift from Japan in 1912.</li>
              <li className={styles.factItem}>Cherry blossoms symbolize both life and death in Japanese culture.</li>
            </ul>
          </div>

          <div className={styles.section}>
            <h3 className={styles.sectionTitle}>Cultural Significance</h3>
            <p className={styles.sectionText}>
              In Japanese culture, cherry blossoms represent the beauty and fragility of life. 
              The blossoms&apos; short lifespan is often compared to human existence. 
              This concept is deeply rooted in Buddhist teachings about the transience of material things.
            </p>
            <p className={styles.sectionText}>
              Beyond Japan, cherry blossoms have become symbols of friendship between nations. 
              Many countries now have cherry blossom festivals, including the United States, Canada, 
              Brazil, Germany, Turkey, and South Korea.
            </p>
          </div>
        </section>

        <FeatureExperience />
      </main>

      <footer className={styles.footer}>
        <div className={styles.footerContainer}>
          <p className={styles.copyright}>
            &copy; {new Date().getFullYear()} Cherry Blossoms Introduction. All rights reserved.
          </p>
          <p className={styles.footerNote}>
            A celebration of nature&apos;s beauty and cultural heritage.
          </p>
        </div>
      </footer>
    </div>
  );
}
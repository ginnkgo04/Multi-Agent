import Image from 'next/image';
import FeatureExperience from '@/components/FeatureExperience';
import { fetchSnacks } from '@/lib/api';
import styles from './page.module.css';

export default async function Home() {
  const snacks = await fetchSnacks();

  return (
    <div className={styles.container}>
      {/* Hero Section */}
      <header className={styles.hero}>
        <div className={styles.heroContent}>
          <h1 className={styles.heroTitle}>武汉特色小吃</h1>
          <p className={styles.heroSubtitle}>探索江城美食文化，品味地道武汉风味</p>
          <div className={styles.heroDecoration}>
            <span className={styles.decorationDot}></span>
            <span className={styles.decorationLine}></span>
            <span className={styles.decorationDot}></span>
          </div>
        </div>
        <div className={styles.heroImage}>
          <Image
            src="/images/hero-bg.jpg"
            alt="武汉小吃集合"
            fill
            priority
            style={{ objectFit: 'cover' }}
          />
        </div>
      </header>

      {/* Introduction Section */}
      <section className={styles.introduction}>
        <div className={styles.sectionHeader}>
          <h2 className={styles.sectionTitle}>武汉美食文化</h2>
          <p className={styles.sectionSubtitle}>九省通衢，百味交融</p>
        </div>
        <div className={styles.introContent}>
          <p>
            武汉，这座位于长江与汉江交汇处的城市，以其独特的地理位置和悠久的历史文化，
            孕育出了丰富多彩的美食文化。武汉小吃融合了南北风味，既有湖北菜的鲜香醇厚，
            又吸收了各地小吃的精华，形成了独具特色的江城风味。
          </p>
          <p>
            从清晨的热干面到深夜的烧烤摊，从街边的豆皮到店里的汤包，
            武汉的小吃不仅是一种食物，更是一种生活方式，一种文化传承。
          </p>
        </div>
      </section>

      {/* Featured Snacks Section */}
      <section className={styles.featuredSnacks}>
        <div className={styles.sectionHeader}>
          <h2 className={styles.sectionTitle}>特色小吃推荐</h2>
          <p className={styles.sectionSubtitle}>不可错过的武汉味道</p>
        </div>
        
        <div className={styles.snacksGrid}>
          {snacks.map((snack) => (
            <div key={snack.id} className={styles.snackCard}>
              <div className={styles.snackImage}>
                <Image
                  src={snack.image_url || `/images/${snack.name.toLowerCase().replace(/\s+/g, '-')}.jpg`}
                  alt={snack.name}
                  fill
                  style={{ objectFit: 'cover' }}
                />
              </div>
              <div className={styles.snackContent}>
                <h3 className={styles.snackName}>{snack.name}</h3>
                <p className={styles.snackDescription}>{snack.description}</p>
                <div className={styles.snackMeta}>
                  <span className={styles.snackCategory}>{snack.category}</span>
                  <span className={styles.snackOrigin}>{snack.origin}</span>
                </div>
                <div className={styles.snackDetails}>
                  <p><strong>主要食材：</strong>{snack.ingredients}</p>
                  <p><strong>特点：</strong>{snack.characteristics}</p>
                  <p><strong>最佳品尝时间：</strong>{snack.best_time}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Food Culture Section */}
      <section className={styles.foodCulture}>
        <div className={styles.cultureContent}>
          <div className={styles.cultureText}>
            <h2 className={styles.cultureTitle}>小吃背后的故事</h2>
            <p>
              武汉的小吃不仅仅是食物，它们承载着城市的历史记忆和人文情怀。
              每一道小吃背后都有一个故事，或是关于手艺人的坚守，或是关于市井生活的变迁。
            </p>
            <p>
              热干面的诞生源于一次偶然的失误，却成就了武汉早餐的代表；
              豆皮的制作工艺传承百年，金黄的外皮下包裹着丰富的内涵；
              面窝的独特形状，见证了武汉人早餐的智慧与创意。
            </p>
            <div className={styles.cultureFeatures}>
              <div className={styles.featureItem}>
                <span className={styles.featureIcon}>🍜</span>
                <h4>早餐文化</h4>
                <p>过早是武汉独特的早餐文化，品种丰富，选择多样</p>
              </div>
              <div className={styles.featureItem}>
                <span className={styles.featureIcon}>🌃</span>
                <h4>夜市传统</h4>
                <p>夜市小吃是武汉夜生活的重要组成部分</p>
              </div>
              <div className={styles.featureItem}>
                <span className={styles.featureIcon}>👨‍🍳</span>
                <h4>手艺传承</h4>
                <p>许多小吃制作技艺被列为非物质文化遗产</p>
              </div>
            </div>
          </div>
          <div className={styles.cultureImage}>
            <Image
              src="/images/culture-bg.jpg"
              alt="武汉小吃文化"
              fill
              style={{ objectFit: 'cover' }}
            />
          </div>
        </div>
      </section>

      {/* Experience Section */}
      <FeatureExperience />

      {/* Map Section */}
      <section className={styles.mapSection}>
        <div className={styles.sectionHeader}>
          <h2 className={styles.sectionTitle}>美食地图</h2>
          <p className={styles.sectionSubtitle}>寻找最地道的武汉味道</p>
        </div>
        <div className={styles.mapContent}>
          <div className={styles.mapInfo}>
            <h3>热门小吃聚集地</h3>
            <ul className={styles.locationList}>
              <li>
                <strong>户部巷</strong>
                <p>武汉最著名的小吃街，汇集了各种传统小吃</p>
              </li>
              <li>
                <strong>吉庆街</strong>
                <p>以夜市大排档闻名，夜晚尤其热闹</p>
              </li>
              <li>
                <strong>江汉路</strong>
                <p>商业街中的美食天堂，新旧小吃交融</p>
              </li>
              <li>
                <strong>万松园</strong>
                <p>本地人常去的美食街区，味道正宗</p>
              </li>
            </ul>
          </div>
          <div className={styles.mapVisual}>
            <div className={styles.mapPlaceholder}>
              <Image
                src="/images/wuhan-map.jpg"
                alt="武汉美食地图"
                fill
                style={{ objectFit: 'cover' }}
              />
              <div className={styles.mapMarker} style={{ top: '30%', left: '40%' }}>
                <span className={styles.markerDot}></span>
                <span className={styles.markerLabel}>户部巷</span>
              </div>
              <div className={styles.mapMarker} style={{ top: '45%', left: '50%' }}>
                <span className={styles.markerDot}></span>
                <span className={styles.markerLabel}>吉庆街</span>
              </div>
              <div className={styles.mapMarker} style={{ top: '60%', left: '55%' }}>
                <span className={styles.markerDot}></span>
                <span className={styles.markerLabel}>江汉路</span>
              </div>
              <div className={styles.mapMarker} style={{ top: '50%', left: '65%' }}>
                <span className={styles.markerDot}></span>
                <span className={styles.markerLabel}>万松园</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className={styles.footer}>
        <div className={styles.footerContent}>
          <div className={styles.footerInfo}>
            <h3>武汉特色小吃</h3>
            <p>传承美食文化，品味江城风味</p>
            <p className={styles.copyright}>© 2024 武汉美食文化展示</p>
          </div>
          <div className={styles.footerLinks}>
            <h4>了解更多</h4>
            <ul>
              <li><a href="#">武汉美食历史</a></li>
              <li><a href="#">小吃制作工艺</a></li>
              <li><a href="#">美食节活动</a></li>
              <li><a href="#">联系我们</a></li>
            </ul>
          </div>
          <div className={styles.footerContact}>
            <h4>关注我们</h4>
            <div className={styles.socialLinks}>
              <a href="#" className={styles.socialLink}>微博</a>
              <a href="#" className={styles.socialLink}>微信</a>
              <a href="#" className={styles.socialLink}>抖音</a>
              <a href="#" className={styles.socialLink}>小红书</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
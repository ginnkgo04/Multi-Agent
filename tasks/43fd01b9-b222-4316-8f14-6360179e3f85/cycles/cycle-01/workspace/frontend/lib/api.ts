// API utilities for Pink Pig website

export interface PigFact {
  id: number;
  title: string;
  description: string;
  emoji: string;
  detail: string;
  likes: number;
}

export interface PigCharacteristic {
  id: number;
  title: string;
  description: string;
  icon: string;
  color: string;
}

export interface GalleryItem {
  id: number;
  emoji: string;
  title: string;
  description: string;
}

// Mock data for development
export const mockPigFacts: PigFact[] = [
  {
    id: 1,
    title: "睡眠专家",
    description: "小猪每天要睡12-14个小时，是真正的睡眠冠军！",
    emoji: "💤",
    detail: "充足的睡眠让小猪保持粉嫩的皮肤和快乐的心情。研究表明，睡眠充足的小猪更聪明、更健康。",
    likes: 42
  },
  {
    id: 2,
    title: "美食家",
    description: "小猪的嗅觉比人类灵敏1000倍，能找到最美味的美食！",
    emoji: "🍎",
    detail: "小猪的鼻子非常灵敏，能闻到地下深处的食物。它们最喜欢吃苹果、胡萝卜和玉米。",
    likes: 38
  },
  {
    id: 3,
    title: "游泳健将",
    description: "别看小猪胖乎乎的，它们其实是天生的游泳高手！",
    emoji: "🏊",
    detail: "小猪天生就会游泳，它们的身体脂肪帮助浮在水面上。在炎热的夏天，小猪特别喜欢在水里玩耍。",
    likes: 29
  },
  {
    id: 4,
    title: "社交达人",
    description: "小猪是非常社会化的动物，喜欢和朋友们一起玩耍！",
    emoji: "👫",
    detail: "小猪会通过不同的叫声和身体语言与同伴交流。它们建立深厚的友谊，甚至会互相按摩。",
    likes: 35
  },
  {
    id: 5,
    title: "聪明绝顶",
    description: "小猪的智商相当于3岁的人类小孩，非常聪明！",
    emoji: "🧠",
    detail: "小猪能学会复杂的任务，记住路线，甚至能玩电子游戏。它们有很好的长期记忆能力。",
    likes: 47
  },
  {
    id: 6,
    title: "爱干净",
    description: "小猪其实很爱干净，它们会在固定的地方上厕所！",
    emoji: "🛁",
    detail: "与普遍认知不同，小猪非常注重卫生。它们不会在自己睡觉和吃饭的地方排泄。",
    likes: 31
  }
];

export const mockCharacteristics: PigCharacteristic[] = [
  {
    id: 1,
    title: "粉嫩皮肤",
    description: "我的皮肤是天然的粉红色，柔软光滑，像棉花糖一样可爱",
    icon: "🌸",
    color: "from-pink-400 to-rose-400"
  },
  {
    id: 2,
    title: "圆圆体型",
    description: "圆滚滚的身体让我看起来更加可爱，也让我能储存更多能量",
    icon: "⚪",
    color: "from-purple-400 to-pink-400"
  },
  {
    id: 3,
    title: "卷卷尾巴",
    description: "我的尾巴总是卷成一个小圈圈，这是我独特的标志",
    icon: "🌀",
    color: "from-rose-400 to-orange-400"
  },
  {
    id: 4,
    title: "大耳朵",
    description: "大大的耳朵让我能听到很远的声音，也能帮我散热",
    icon: "👂",
    color: "from-blue-400 to-cyan-400"
  },
  {
    id: 5,
    title: "湿湿鼻子",
    description: "湿润的鼻子让我有超强的嗅觉，能找到最好吃的食物",
    icon: "👃",
    color: "from-green-400 to-emerald-400"
  },
  {
    id: 6,
    title: "快乐性格",
    description: "我天生乐观开朗，总是用微笑面对每一天",
    icon: "😊",
    color: "from-yellow-400 to-amber-400"
  }
];

export const mockGalleryItems: GalleryItem[] = [
  {
    id: 1,
    emoji: "🐷",
    title: "早晨散步",
    description: "在草地上享受阳光"
  },
  {
    id: 2,
    emoji: "🛁",
    title: "洗澡时间",
    description: "保持干净很重要"
  },
  {
    id: 3,
    emoji: "🍎",
    title: "美食时间",
    description: "新鲜的苹果最好吃"
  },
  {
    id: 4,
    emoji: "💤",
    title: "午睡时光",
    description: "美美地睡个午觉"
  },
  {
    id: 5,
    emoji: "🎵",
    title: "音乐时间",
    description: "跟着节奏摇摆"
  },
  {
    id: 6,
    emoji: "🎨",
    title: "艺术创作",
    description: "用泥巴画画"
  },
  {
    id: 7,
    emoji: "🏆",
    title: "获奖时刻",
    description: "最可爱小猪奖"
  },
  {
    id: 8,
    emoji: "❤️",
    title: "爱心满满",
    description: "给朋友们送爱心"
  }
];

// API Service Functions
export class PinkPigApi {
  private static readonly BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api';

  // Get all pig facts
  static async getPigFacts(): Promise<PigFact[]> {
    // In a real app, this would be a fetch call
    // const response = await fetch(`${this.BASE_URL}/facts`);
    // return response.json();
    
    // For now, return mock data
    return new Promise(resolve => {
      setTimeout(() => resolve(mockPigFacts), 300);
    });
  }

  // Like a pig fact
  static async likePigFact(factId: number): Promise<{ success: boolean; likes: number }> {
    // In a real app:
    // const response = await fetch(`${this.BASE_URL}/facts/${factId}/like`, {
    //   method: 'POST',
    // });
    // return response.json();
    
    // Mock implementation
    const fact = mockPigFacts.find(f => f.id === factId);
    if (fact) {
      fact.likes += 1;
      return Promise.resolve({ success: true, likes: fact.likes });
    }
    return Promise.resolve({ success: false, likes: 0 });
  }

  // Get pig characteristics
  static async getCharacteristics(): Promise<PigCharacteristic[]> {
    return new Promise(resolve => {
      setTimeout(() => resolve(mockCharacteristics), 200);
    });
  }

  // Get gallery items
  static async getGalleryItems(): Promise<GalleryItem[]> {
    return new Promise(resolve => {
      setTimeout(() => resolve(mockGalleryItems), 200);
    });
  }

  // Download resources
  static async downloadResource(type: 'wallpaper' | 'coloring' | 'sticker'): Promise<{ url: string }> {
    // Mock download URLs
    const urls = {
      wallpaper: '/downloads/pink-pig-wallpaper.jpg',
      coloring: '/downloads/pink-pig-coloring.pdf',
      sticker: '/downloads/pink-pig-stickers.zip'
    };

    return new Promise(resolve => {
      setTimeout(() => resolve({ url: urls[type] }), 500);
    });
  }

  // Share on social media
  static async shareOnSocial(platform: 'twitter' | 'facebook' | 'wechat'): Promise<{ success: boolean }> {
    const shareUrls = {
      twitter: `https://twitter.com/intent/tweet?text=看看这只可爱的粉色小猪！&url=${window.location.href}`,
      facebook: `https://www.facebook.com/sharer/sharer.php?u=${window.location.href}`,
      wechat: '#' // WeChat sharing requires special handling
    };

    if (platform === 'wechat') {
      // WeChat sharing would require QR code generation
      return Promise.resolve({ success: true });
    }

    window.open(shareUrls[platform], '_blank');
    return Promise.resolve({ success: true });
  }

  // Play pig sound
  static async playPigSound(): Promise<void> {
    // In a real app, this would play an audio file
    console.log("Oink oink! 🐷");
    
    // Example with Web Audio API:
    // const audioContext = new AudioContext();
    // const oscillator = audioContext.createOscillator();
    // oscillator.type = 'sine';
    // oscillator.frequency.setValueAtTime(200, audioContext.currentTime);
    // oscillator.connect(audioContext.destination);
    // oscillator.start();
    // oscillator.stop(audioContext.currentTime + 0.5);
    
    return Promise.resolve();
  }
}

// Utility functions
export function formatNumber(num: number): string {
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'k';
  }
  return num.toString();
}

export function getRandomPigEmoji(): string {
  const emojis = ['🐷', '🐽', '🐖', '🐗', '👃', '🌸', '💕', '🎀'];
  return emojis[Math.floor(Math.random() * emojis.length)];
}

export function generatePigName(): string {
  const names = ['粉粉', '猪猪', '小可爱', '胖胖', '嘟嘟', '圆圆', '糖糖', '泡泡'];
  return names[Math.floor(Math.random() * names.length)];
}

// Local storage utilities for user preferences
export class UserPreferences {
  private static readonly STORAGE_KEY = 'pink-pig-preferences';

  static getPreferences(): {
    soundEnabled: boolean;
    likedFacts: number[];
    theme: 'light' | 'dark' | 'pink';
  } {
    if (typeof window === 'undefined') {
      return {
        soundEnabled: true,
        likedFacts: [],
        theme: 'pink'
      };
    }

    const stored = localStorage.getItem(this.STORAGE_KEY);
    if (stored) {
      return JSON.parse(stored);
    }

    return {
      soundEnabled: true,
      likedFacts: [],
      theme: 'pink'
    };
  }

  static savePreferences(prefs: {
    soundEnabled: boolean;
    likedFacts: number[];
    theme: 'light' | 'dark' | 'pink';
  }): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(prefs));
    }
  }

  static toggleSound(): boolean {
    const prefs = this.getPreferences();
    prefs.soundEnabled = !prefs.soundEnabled;
    this.savePreferences(prefs);
    return prefs.soundEnabled;
  }

  static toggleLikeFact(factId: number): number[] {
    const prefs = this.getPreferences();
    if (prefs.likedFacts.includes(factId)) {
      prefs.likedFacts = prefs.likedFacts.filter(id => id !== factId);
    } else {
      prefs.likedFacts.push(factId);
    }
    this.savePreferences(prefs);
    return prefs.likedFacts;
  }
}
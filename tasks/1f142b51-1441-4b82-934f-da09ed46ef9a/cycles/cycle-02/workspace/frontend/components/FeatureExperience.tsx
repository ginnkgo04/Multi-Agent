'use client';

import { useState } from 'react';
import Image from 'next/image';

interface FunFact {
  id: number;
  title: string;
  description: string;
  icon: string;
}

interface GalleryImage {
  id: number;
  src: string;
  alt: string;
  caption: string;
}

export default function FeatureExperience() {
  const [activeTab, setActiveTab] = useState<'facts' | 'gallery'>('facts');
  const [selectedImage, setSelectedImage] = useState<number | null>(null);

  const funFacts: FunFact[] = [
    {
      id: 1,
      title: 'Not Actually a Panda',
      description: 'Red pandas are more closely related to raccoons and weasels than to giant pandas. They were named "panda" first, about 50 years before the giant panda!',
      icon: '🐾',
    },
    {
      id: 2,
      title: 'False Thumb',
      description: 'Red pandas have a "false thumb" — an extended wrist bone that helps them grip bamboo and climb trees with ease.',
      icon: '✋',
    },
    {
      id: 3,
      title: 'Thermoregulation',
      description: 'They use their bushy tails as blankets to keep warm in cold mountain climates. The tail can be as long as their body!',
      icon: '🧣',
    },
    {
      id: 4,
      title: 'Solitary Creatures',
      description: 'Red pandas are mostly solitary except during mating season. They communicate through scent marking and various vocalizations.',
      icon: '🗣️',
    },
  ];

  const galleryImages: GalleryImage[] = [
    {
      id: 1,
      src: '/images/red-panda-1.jpg',
      alt: 'Red panda resting on a tree branch',
      caption: 'Resting on a tree branch',
    },
    {
      id: 2,
      src: '/images/red-panda-2.jpg',
      alt: 'Red panda eating bamboo',
      caption: 'Enjoying bamboo meal',
    },
    {
      id: 3,
      src: '/images/red-panda-3.jpg',
      alt: 'Red panda climbing a tree',
      caption: 'Expert climber in action',
    },
    {
      id: 4,
      src: '/images/red-panda-4.jpg',
      alt: 'Red panda curled up sleeping',
      caption: 'Cozy sleeping position',
    },
  ];

  const handleImageClick = (id: number) => {
    setSelectedImage(id === selectedImage ? null : id);
  };

  return (
    <section className="feature-experience py-12 px-4 md:px-8 bg-gradient-to-b from-amber-50 to-white">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-10">
          <h2 className="text-3xl md:text-4xl font-bold text-amber-900 mb-4">
            Interactive Features
          </h2>
          <p className="text-lg text-amber-700 max-w-3xl mx-auto">
            Explore fun facts and browse our red panda gallery. Click on images to see them larger!
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="flex justify-center mb-8">
          <div className="inline-flex rounded-lg border border-amber-300 p-1 bg-white shadow-sm">
            <button
              onClick={() => setActiveTab('facts')}
              className={`px-6 py-3 rounded-md text-lg font-medium transition-all ${activeTab === 'facts'
                  ? 'bg-amber-500 text-white shadow'
                  : 'text-amber-700 hover:bg-amber-100'
                }`}
            >
              🐼 Fun Facts
            </button>
            <button
              onClick={() => setActiveTab('gallery')}
              className={`px-6 py-3 rounded-md text-lg font-medium transition-all ${activeTab === 'gallery'
                  ? 'bg-amber-500 text-white shadow'
                  : 'text-amber-700 hover:bg-amber-100'
                }`}
            >
              📸 Photo Gallery
            </button>
          </div>
        </div>

        {/* Content Area */}
        <div className="bg-white rounded-2xl shadow-xl p-6 md:p-8 border border-amber-200">
          {activeTab === 'facts' ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {funFacts.map((fact) => (
                <div
                  key={fact.id}
                  className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-xl p-6 border border-amber-200 hover:border-amber-300 transition-all hover:shadow-md"
                >
                  <div className="flex items-start gap-4">
                    <div className="text-3xl bg-white p-3 rounded-full shadow-sm">
                      {fact.icon}
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-amber-900 mb-2">
                        {fact.title}
                      </h3>
                      <p className="text-amber-800 leading-relaxed">
                        {fact.description}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                {galleryImages.map((image) => (
                  <div
                    key={image.id}
                    className={`relative overflow-hidden rounded-xl cursor-pointer transition-all duration-300 ${selectedImage === image.id
                        ? 'ring-4 ring-amber-500 ring-offset-2 scale-[1.02]'
                        : 'hover:scale-[1.03] hover:shadow-lg'
                      }`}
                    onClick={() => handleImageClick(image.id)}
                  >
                    <div className="aspect-square relative bg-gradient-to-br from-amber-100 to-orange-100">
                      {/* Placeholder for actual images */}
                      <div className="absolute inset-0 flex items-center justify-center">
                        <div className="text-center">
                          <div className="text-5xl mb-2">🖼️</div>
                          <p className="text-sm text-amber-700 font-medium">
                            {image.alt}
                          </p>
                        </div>
                      </div>
                    </div>
                    <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-4">
                      <p className="text-white font-medium text-sm">
                        {image.caption}
                      </p>
                    </div>
                    {selectedImage === image.id && (
                      <div className="absolute top-2 right-2 bg-amber-500 text-white rounded-full w-8 h-8 flex items-center justify-center">
                        ✓
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {selectedImage && (
                <div className="bg-gradient-to-r from-amber-50 to-orange-50 rounded-xl p-6 border border-amber-300">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="text-2xl">🔍</div>
                    <h3 className="text-xl font-bold text-amber-900">
                      Selected Image Details
                    </h3>
                  </div>
                  <p className="text-amber-800">
                    <strong>Description:</strong>{' '}
                    {galleryImages.find(img => img.id === selectedImage)?.alt}
                  </p>
                  <p className="text-amber-800 mt-2">
                    <strong>Caption:</strong>{' '}
                    {galleryImages.find(img => img.id === selectedImage)?.caption}
                  </p>
                  <button
                    onClick={() => setSelectedImage(null)}
                    className="mt-4 px-4 py-2 bg-amber-500 text-white rounded-lg hover:bg-amber-600 transition-colors"
                  >
                    Clear Selection
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Interactive Stats */}
          <div className="mt-10 pt-8 border-t border-amber-200">
            <div className="flex flex-wrap justify-center gap-8">
              <div className="text-center">
                <div className="text-3xl font-bold text-amber-600">4</div>
                <div className="text-amber-700 font-medium">Fun Facts</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-amber-600">{galleryImages.length}</div>
                <div className="text-amber-700 font-medium">Gallery Images</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-amber-600">
                  {selectedImage ? '1' : '0'}
                </div>
                <div className="text-amber-700 font-medium">Selected</div>
              </div>
            </div>
          </div>
        </div>

        {/* Call to Action */}
        <div className="text-center mt-10">
          <p className="text-amber-700 mb-4">
            Want to learn more about red panda conservation?
          </p>
          <button className="px-8 py-3 bg-gradient-to-r from-amber-500 to-orange-500 text-white font-bold rounded-full shadow-lg hover:shadow-xl transition-all hover:scale-105">
            Support Conservation Efforts
          </button>
        </div>
      </div>
    </section>
  );
}
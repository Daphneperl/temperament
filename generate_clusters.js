const fs = require('fs');
const path = require('path');

const IMAGE_DIR = 'images';
const OUTPUT_FILE = 'semantic_clusters.json';
const NUM_CLUSTERS = process.argv[2] ? parseInt(process.argv[2]) : 10;

if (isNaN(NUM_CLUSTERS) || NUM_CLUSTERS <= 0) {
  console.error('❌ Please provide a valid number of clusters.');
  process.exit(1);
}

const getClusterName = index => `Cluster_${index}`;

const run = () => {
  const files = fs.readdirSync(IMAGE_DIR).filter(f =>
    /\.(jpg|jpeg|png|gif)$/i.test(f)
  );

  const images = {};
  const clusters = {};

  files.forEach((filename, i) => {
    const clusterId = i % NUM_CLUSTERS;
    images[filename] = i;
    clusters[i] = getClusterName(clusterId);
  });

  const output = { images, clusters };
  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(output, null, 2));
  console.log(`✅ ${OUTPUT_FILE} created with ${files.length} images across ${NUM_CLUSTERS} clusters.`);
};

run();

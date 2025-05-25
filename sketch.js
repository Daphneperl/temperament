/* ---------- tuning ---------- */
const CYL_RADIUS        = 1800;        // base radius
const SECTOR_WIDTH      = Math.PI/6;   // angular span per cluster
const RING_PITCH        = 650;         // vertical spacing
const JITTER_R          = 400;         // radial scatter  (↑ = looser)
const JITTER_Y          = 300;         // vertical scatter (↑ = looser)
const THUMB_SIZE        = 220;
const TITLE_UPSHIFT     = 400;         // how high label sits above median Y
const IMAGE_FOLDER      = "images/";

/* ---------- globals ---------- */
let hemiFont, clusterData;
let labelInfo = [];      // {name, ang, midY, tex}
let nodes     = [];      // thumbnails
let camAng=0, camH=0, camZoom=1400;
let lastMouse, ready=false;

/* ---------- preload ---------- */
function preload(){
  hemiFont   = loadFont("Heming.ttf");      // ensure the file exists in root
  clusterData= loadJSON("semantic_clusters.json");
}

/* ---------- setup ---------- */
function setup(){
  createCanvas(windowWidth,windowHeight,WEBGL);
  noStroke(); textureMode(NORMAL);
  perspective(Math.PI/3, width/height, 1, 25000);

  /* distinct labels → labelInfo --------------------------------------- */
  const labels = [...new Set(Object.values(clusterData.clusters))];
  const step   = TWO_PI / labels.length;

  labels.forEach((lab,i)=>{
    const g = createGraphics(600,100);
    g.clear();
    g.textFont(hemiFont);
    g.textStyle(BOLD);
    g.textAlign(CENTER,CENTER);
    g.textSize(48);
    g.fill(255);
    g.text(lab, 300, 50);

    labelInfo.push({
      name : lab,
      ang  : i*step,
      midY : -((labels.length-1)*RING_PITCH)/2 + i*RING_PITCH,
      tex  : g
    });
  });

  /* load images -------------------------------------------------------- */
  const files = Object.keys(clusterData.images);
  let loaded=0;
  files.forEach(f=>{
    loadImage(IMAGE_FOLDER+f,img=>{
      const lbl = clusterData.clusters[ clusterData.images[f] ];
      const inf = labelInfo.find(l=>l.name===lbl);

      const ang = inf.ang + random(-SECTOR_WIDTH/2, SECTOR_WIDTH/2);
      const rad = CYL_RADIUS + random(-JITTER_R, JITTER_R);
      const y   = inf.midY + random(-JITTER_Y, JITTER_Y);

      nodes.push({
        img,
        base: createVector(rad*cos(ang), y, rad*sin(ang)),
        phaseR: random(TWO_PI),
        phaseY: random(TWO_PI)
      });

      if(++loaded===files.length) ready=true;
    },()=>{ if(++loaded===files.length) ready=true; });
  });
}

/* ---------- draw ---------- */
function draw(){
  if(!ready) return;
  clear();

  const camX = camZoom*sin(camAng), camZ = camZoom*cos(camAng);
  camera(camX,camH,camZ, 0,camH,0, 0,1,0);
  const eye = createVector(camX,camH,camZ);

  /* thumbnails -------------------------------------------------------- */
  [...nodes].sort((a,b)=>p5.Vector.dist(eye,b.base)-p5.Vector.dist(eye,a.base))
    .forEach(n=>{
      const t=frameCount*0.003;
      const pos = p5.Vector.add(n.base,
        createVector( 60*sin(t+n.phaseR),
                      40*sin(t*0.8+n.phaseY),
                      60*cos(t+n.phaseR)));
      const yaw = atan2(eye.x-pos.x, eye.z-pos.z);

      push();
        translate(pos); rotateY(yaw);
        const h = THUMB_SIZE*n.img.height/n.img.width;
        texture(n.img); plane(THUMB_SIZE,h);
      pop();
    });

  /* titles ------------------------------------------------------------ */
  labelInfo.forEach(inf=>{
    const p = createVector(
      CYL_RADIUS * cos(inf.ang),
      inf.midY + TITLE_UPSHIFT,
      CYL_RADIUS * sin(inf.ang)
    );
    push();
      translate(p); rotateY(camAng);
      texture(inf.tex); plane(600,100);
    pop();
  });
}

/* ---------- interaction ---------- */
function mousePressed(){ lastMouse=createVector(mouseX,mouseY); }
function mouseDragged(){
  if(mouseButton===LEFT){
    const dx=mouseX-lastMouse.x, dy=mouseY-lastMouse.y;
    camAng -= dx*0.005;
    camH    = constrain(camH - dy*2, -6000, 6000);
    lastMouse.set(mouseX,mouseY);
  }
}
function mouseWheel(e){ camZoom = constrain(camZoom + e.delta*2, 300, 4000); return false; }
function windowResized(){ resizeCanvas(windowWidth,windowHeight);
                          perspective(Math.PI/3, width/height, 1, 25000); }

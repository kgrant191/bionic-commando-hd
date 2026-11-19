// Compare the recorded actor coordinates to opaque paint samples in the real Mesen frame buffer.
#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <string>
#include <vector>
extern "C" uint32_t* output(void*) asm("_ZN15BaseVideoFilter15GetOutputBufferEv");
extern "C" void capture(void*,int,void*,void*) asm("_ZN15BaseVideoFilter14TakeScreenshotE15VideoFilterTypeNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEPNS1_18basic_stringstreamIcS4_S5_EE");
struct Signature{int blue,face,k,x,y;uint32_t a,b,c,d;};
static const Signature markers[]={
{0,0,0,52,-122,14008729,65536,14993305,16772042},
{0,0,1,28,-99,6237726,12150850,6701610,14795662},
{0,0,2,52,-70,9598010,13609312,16770973,2},
{0,0,4,18,-16,2365964,3811087,15236932,16766874},
{0,0,5,-24,-6,393985,5519918,16558959,16758135},
{0,0,6,8,20,9269822,11573335,2167819,2164744},
{0,0,7,16,57,5393238,394759,12301243,3814715},
{0,1,0,46,-130,13086339,262913,15716513,16769720},
{0,1,1,50,-99,12740670,9124644,16113074,10765606},
{0,1,2,-28,-84,7163956,11769196,2099968,15129528},
{0,1,3,-26,-54,5192479,5588782,3680532,11965789},
{0,1,4,-22,-16,3023374,2036230,16769448,16758650},
{0,1,5,24,-2,16755561,852993,16292447,5447951},
{0,1,6,-10,18,5917480,0,11572561,3812894},
{0,1,7,-14,51,394759,2170917,2960435,8947336},
{1,0,0,52,-122,14008729,65536,14993305,16772042},
{1,0,1,28,-99,6237726,12150850,6701610,14795662},
{1,0,2,52,-70,9598010,13609312,16770973,2},
{1,0,4,18,-16,2365964,3811087,15236931,16766874},
{1,0,5,-24,-6,328450,5323826,16624238,16627064},
{1,0,6,6,20,594464,9335100,5277111,1318439},
{1,0,7,16,57,5393238,394759,12301243,3814715},
{1,1,0,46,-130,13086339,262913,15716513,16769720},
{1,1,1,50,-99,12740670,9124644,16113074,10765606},
{1,1,2,-28,-84,7163956,11769196,2099968,15129528},
{1,1,3,-26,-54,5192479,5588782,3680532,11965789},
{1,1,4,-22,-16,3023374,2036230,16769448,16758907},
{1,1,5,24,-2,16755304,853250,16292447,5447952},
{1,1,6,-10,18,5917738,0,11572560,3289132},
{1,1,7,-14,51,460295,2170917,2960435,8947336},
};
bool near(uint32_t a,uint32_t b){
 for(int shift:{0,8,16})if(std::abs(int((a>>shift)&255)-int((b>>shift)&255))>3)return false;
 return true;
}
extern "C" void capture(void* filter,int,void*,void*){
 static std::string root=getenv("A14_RUN");
 static unsigned n=std::atoi(getenv("FRAME_BASE"));
 static FILE* ram=fopen(getenv("A8_RAM"),"rb");
 static FILE* report=fopen((root+"/flight.tsv").c_str(),"w");
 static FILE* clips=fopen((root+"/clips.raw").c_str(),"wb");
 ++n;uint32_t* screen=output(filter);unsigned char state[2048];
 fseek(ram,2048L*(n-1),SEEK_SET);if(fread(state,2048,1,ram)!=1)return;
 for(int i=8;i<=10;i++){
  int pose=state[0x5e4+i];if((pose!=0x92 && pose!=0xb0)||state[0x536+i]!=1||state[0x55c+i]||state[0x596+i]||state[0xff]!=0x1a||state[0x4d]!=8)continue;
  int cx=4*(state[0x56f+i]&252),cy=4*((state[0x5a9+i]&254)-8);
  int face=state[0x633+i]&1,best=0,possible=0,bx=0,by=0;
  for(int dy=-8;dy<=8;dy+=4)for(int dx=-8;dx<=8;dx+=4){
   int hits=0,inside=0;
   for(auto& s:markers){
    if(s.blue!=(pose==0xb0)||s.face!=face)continue;
    int x=cx+dx+s.x,y=cy+dy+s.y;if(x<0||x+2>=1024||y<0||y+2>=896)continue;
    auto p=screen+1024*y+x;inside++;
    if(near(p[0],s.a)&&near(p[2],s.b)&&near(p[2048],s.c)&&near(p[2050],s.d))hits++;
   }
   if(dx==0&&dy==0)possible=inside;
   if(hits>best){best=hits;bx=dx;by=dy;}
  }
  fprintf(report,"%u %d %d %d %d %d %d %d %d %d\n",n,i,pose,cx,cy,face,possible,best,bx,by);
 }
 if((n>=1840 && n<=2030)||(n>=10385&&n<=10548)||(n>=22312&&n<=22540)){
  fwrite(&n,4,1,clips);
  static uint32_t scaled[512*448];
  for(int y=0;y<448;y++)for(int x=0;x<512;x++)scaled[y*512+x]=screen[(2*y)*1024+2*x];
  fwrite(scaled,sizeof scaled,1,clips);
 }
 if(n==21216||n==22368||n==22512||n==17496||n==13392||n==9408||n==10462||n==1904){
  FILE* snap=fopen((root+"/"+std::to_string(n)+".bgra").c_str(),"wb");
  fwrite(screen,1024*896*4,1,snap);fclose(snap);
 }
 if(n%120==0){fflush(report);fflush(clips);}
}

// Build with c++ -O2 -std=c++17 -shared -fPIC fallback_probe.cpp -o probe.so.
// For the Area 8 headless replay, select all frames for screenshot capture and
// set LD_PRELOAD to probe.so, A14_RUN to the replay directory, and REG8_LIMIT
// to the number of pairs printed by probe_v0151.py. The replay calls the
// capture hook once per frame. This diagnostic substitutes a TSV for the PNGs.
#include <cstdio>
#include <cstdint>
#include <cstdlib>
#include <string>
#include <vector>

extern "C" uint32_t* buffer(void*) asm("_ZN15BaseVideoFilter15GetOutputBufferEv");
extern "C" void sample(void*,int,void*,void*) asm("_ZN15BaseVideoFilter14TakeScreenshotE15VideoFilterTypeNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEPNS1_18basic_stringstreamIcS4_S5_EE");
extern "C" void sample(void* filter, int, void*, void*) {
    static int frame=0;
    ++frame;
    static FILE* log=std::fopen((std::string(std::getenv("A14_RUN"))+"/matched.tsv").c_str(),"w");
    static const int limit=std::atoi(std::getenv("REG8_LIMIT"));
    static std::vector<int> count(limit), first_x(limit), first_y(limit), seen;
    const uint32_t* pixels=buffer(filter);
    // Area 8 captures use 4x output with eight NES overscan lines cropped at either edge.
    for (int y=2; y<896; y+=4) {
        for (int x=2; x<1024; x+=4) {
            const uint32_t pixel=pixels[y*1024+x];
            const int red=(pixel>>16)&255, green=(pixel>>8)&255;
            if (red!=255 || green<2 || green>2+(limit>>8) ||
                (pixels[y*1024+x+1]&0xffffff)!=0x05f19e) continue;
            const int index=(green-2)*256+(pixel&255);
            if (index>=limit) continue;
            if (count[index]++==0) {
                seen.push_back(index);
                first_x[index]=x/4;
                first_y[index]=y/4+8;
            }
        }
    }
    for (int index:seen) {
        std::fprintf(log,"%d %d %d %d %d\n",frame,index,count[index],first_x[index],first_y[index]);
        count[index]=0;
    }
    seen.clear();
    if (frame%120==0) std::fflush(log);
}

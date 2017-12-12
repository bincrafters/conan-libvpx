#include <cstdlib>
#include <iostream>
#include "vpx/vpx_codec.h"

int main()
{
    std::cout << "vpx version " << vpx_codec_version_str() << std::endl;
    return EXIT_SUCCESS;
}

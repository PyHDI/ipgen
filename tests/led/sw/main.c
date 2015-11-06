#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include "umem.h"
#include "ipgen.h"

void usage()
{
  printf("usage: led -v <value>\n");
}

int main(int argc, char *argv[])
{
  int c;
  int value = 0xff;

  while ((c = getopt(argc, argv, "v:h")) != -1) {
    switch(c) {
    case 'v':
      value = atoi(optarg);
      break;
    case 'h':
      usage();
      return 0;
    default:
      printf("invalid option: %c\n", c);
      usage();
      return -1;
    }
  }

  umem_open();
  ipgen_open();

  ipgen_write_4b((unsigned int)value);

  unsigned int read_value;
  ipgen_read_4b(&read_value);

  printf("LED: %x\n", read_value);

  umem_close();
  ipgen_close();

  return 0;
}


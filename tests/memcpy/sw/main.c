#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include "umem.h"
#include "ipgen.h"

void usage()
{
  printf("usage: memcpy [-s <size>] [-v <value>] [-c] [-h]\n");
}

int main(int argc, char *argv[])
{
  int c;
  int value = 0;
  int check = 0;
  unsigned int size = 1024;

  while ((c = getopt(argc, argv, "s:v:ch")) != -1) {
    switch(c) {
    case 's':
      size = atoi(optarg);
      break;
    case 'v':
      value = atoi(optarg);
      break;
    case 'c':
      check = 1;
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

  volatile int *a = (volatile int*) umem_malloc(sizeof(int) * size);
  volatile int *b = (volatile int*) umem_malloc(sizeof(int) * size);

  int i;

  if(check) goto verify;

  // initialization of data
  for(i=0; i<size; i++){
    a[i] = i + value;
    b[i] = 0;
  }

  umem_cache_clean((char*)a, sizeof(int) * size);
  umem_cache_clean((char*)b, sizeof(int) * size);

  unsigned int src = umem_get_physical_address((void*)a);
  unsigned int dst = umem_get_physical_address((void*)b);

  printf("memcpy from src to dst\n");
  printf("src  = %08x\n", src);
  printf("dst  = %08x\n", dst);
  printf("size = %8d\n", size);

  ipgen_write_4b(size);
  printf(".");
  ipgen_write_4b(src);
  printf(".");
  ipgen_write_4b(dst);
  printf(".\n");

  unsigned int read_value;
  ipgen_read_4b(&read_value);

 verify:
  if(check){
    printf("check only\n");
  }

  umem_cache_clean((char*)a, sizeof(int) * size);
  umem_cache_clean((char*)b, sizeof(int) * size);

  int mismatch = 0;
  for(i=0; i<size; i++){
    //printf("read  %10d\n", b[i]);
    if(a[i] != b[i]){
      mismatch = 1;
      printf("%10d %10d\n", a[i], b[i]);
    }
    if(i==size-1){
      //printf("read  %10d\n", b[i]);
    }
  }

  if(mismatch){
    printf("NG\n");
  }else{
    printf("OK\n");
  }

  umem_close();
  ipgen_close();

  return 0;
}


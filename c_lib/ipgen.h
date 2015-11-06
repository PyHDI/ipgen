#ifndef IPGEN_H
#define IPGEN_H

#define UIO_IPGEN "/dev/uio1"
#define IPGEN_SIZE (0x00001000)

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <assert.h>
#include <sys/mman.h>
#include <fcntl.h>

int fd_ipgen = -1;
volatile int* ipgen_ptr = NULL;

void ipgen_open()
{
  fd_ipgen = open(UIO_IPGEN, O_RDWR);
  if(fd_ipgen < 1){
    printf("Invalid UIO device file: '%s'\n", UIO_IPGEN);
    exit(1);
  }
  ipgen_ptr = (volatile int*) mmap(NULL, IPGEN_SIZE, PROT_READ|PROT_WRITE, MAP_SHARED, fd_ipgen, 0);
}

void ipgen_write_4b(unsigned int data)
{
  *ipgen_ptr = (volatile unsigned int) data;
}

void ipgen_read_4b(unsigned int* data)
{
  volatile unsigned int r = *ipgen_ptr;
  *data = r;
}

void ipgen_close()
{
  if(ipgen_ptr == NULL){
    printf("ipgen_close(): UIO is not opened.\n");
    return;
  }
  munmap((void*) ipgen_ptr, IPGEN_SIZE);
  ipgen_ptr = NULL;
  close(fd_ipgen);
  fd_ipgen = -1;
}

#endif

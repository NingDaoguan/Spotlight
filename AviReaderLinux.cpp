/*
   g++ -I/usr/include/avifile AviReaderLinux.cpp -laviplay -o AviReader
*/

#include <avifile.h>
#include <aviplay.h>
#include <fourcc.h>
#include <except.h>
#include <utils.h>
#include <version.h>
#include <image.h>
#include <avm_output.h>

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

// write an error message instead of the image and exit
void writeError(char *outFileName, char *message) {
  printf("%s", message);

  FILE *fp;
  fp = fopen(outFileName, "wb");

  // 4 byte little endian integers
  int errorCode = 4; // offset to start of error message
  int length = strlen(message);
  fwrite(&errorCode, 4, 1, fp);
  fwrite(message, length, 1, fp);
  fclose(fp);

  exit(1);
}

int main (int argc, char* argv[]) {
  char errorBuf[1000];

  if (argc != 4) {
    printf("usage:\n  %s inputAVIfile outputImage frameNumber\n", argv[0]);
    exit(1);
  }
  long frameNumber = atol(argv[3]);

  try {
    // disable most avifile informational messages
    avm::out.setDebugLevel(0, -1);

    // sanity check
    if (GetAvifileVersion() != AVIFILE_VERSION) {
      int i = 0;
      i += sprintf(&errorBuf[i], "This binary was compiled for Avifile ver. %f", AVIFILE_VERSION);
      i += sprintf(&errorBuf[i], ", but the library is ver. %f\n", GetAvifileVersion());
      i += sprintf(&errorBuf[i], "Aborting.\n");
      writeError(argv[2], errorBuf);
    }

    IAviReadFile* aviFile = CreateIAviReadFile (argv[1]);
    if (aviFile == 0) {
      sprintf(errorBuf, "AviReader: Could not open file: %s\n", argv[1]);
      writeError(argv[2], errorBuf);
    }

    int result = aviFile->VideoStreamCount();
    //printf("VideoStreamCount(): %d\n", result);
    if (result < 1) {
      delete aviFile;
      sprintf(errorBuf, "AviReader: No video data in file: %s\n", argv[1]);
      writeError(argv[2], errorBuf);
    }

    IAviReadStream* videoStream = aviFile->GetStream(0, AviStream::Video);
    if (videoStream == 0) {
      delete aviFile;
      sprintf(errorBuf, "AviReader: Could not get video stream from file: %s\n", argv[1]);
      writeError(argv[2], errorBuf);
    }

    StreamInfo* streamInfo = videoStream->GetStreamInfo();
    int videoWidth = streamInfo->GetVideoWidth();
    int videoHeight = streamInfo->GetVideoHeight();
    long videoFrames = streamInfo->GetStreamFrames();
    //printf("frames: %ld, width: %d, height: %d\n", videoFrames, videoWidth, videoHeight);
    delete streamInfo;

    if (frameNumber < 0) {
      delete aviFile;
      sprintf(errorBuf, "AviReader: Frame requested is less than 0\n");
      writeError(argv[2], errorBuf);
    }

    if (frameNumber > videoFrames) {
      delete aviFile;
      sprintf(errorBuf, "AviReader: Frame requested is past end of file\n");
      writeError(argv[2], errorBuf);
    }

    result = videoStream->StartStreaming();
    //printf("StartStreaming() : %ld\n", result);
    if (result < 0) {
      delete aviFile;
      sprintf(errorBuf, "AviReader: Could not decode video. Is the correct codec installed?\n");
      writeError(argv[2], errorBuf);
    }

    //printf("Seeking to %ld\n", frameNumber);
    videoStream->Seek(frameNumber);
    videoStream->SeekToPrevKeyFrame();
    int previousKeyFrame = videoStream->GetPos();
    //printf("Previous key frame: %ld\n", previousKeyFrame);
    for (;previousKeyFrame<frameNumber;previousKeyFrame++)
      videoStream->ReadFrame(true);
    result = videoStream->GetPos();
    //printf("Current frame: %ld\n", result);

    CImage* image = videoStream->GetFrame(true);
    image->ToRGB();
    image->ByteSwap();
    // flip upside down image
    int i = 0;
    int h = image->Height()-1;
    int line = image->Width()*3;
    char *buf =(char *) malloc(line);
    char *data = (char *) image->Data();
    while (i < h) {
      memcpy(buf, data+i*line, line);
      memcpy(data+i*line, data+h*line, line);
      memcpy(data+h*line, buf, line);
      i++;
      h--;
    }
    free(buf);

    FILE *fp;
    fp = fopen(argv[2], "wb");

    // Write the header
    // 4 byte little endian integers
    int errorCode = 0;
    int colorPlanes = 3;
    int bitsPerPlane = 8;
    fwrite(&errorCode, 4, 1, fp);
    fwrite(&videoFrames, 4, 1, fp);
    fwrite(&videoWidth, 4, 1, fp);
    fwrite(&videoHeight, 4, 1, fp);
    fwrite(&colorPlanes, 4, 1, fp);
    fwrite(&bitsPerPlane, 4, 1, fp);

    // Write the data
    fwrite(image->Data(), 1, image->Bytes(), fp);

    fclose(fp);

    image->Release();
    videoStream->StopStreaming();
    delete aviFile;

  } catch(const char* string) {
    writeError(argv[2], (char*)string);
  }
  return 0;
}

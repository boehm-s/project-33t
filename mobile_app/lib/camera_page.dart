import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:flutter/cupertino.dart';
import 'dart:developer';
import 'dart:io';
import 'dart:math';
import 'package:flutter/rendering.dart';
import 'package:image/image.dart' as IMG;
import 'package:path/path.dart' as Path;

import 'preview_page.dart';

class CameraPage extends StatefulWidget {
  const CameraPage({Key? key, required this.cameras}) : super(key: key);

  final List<CameraDescription>? cameras;

  @override
  State<CameraPage> createState() => _CameraPageState();
}

class _CameraPageState extends State<CameraPage> {
  late CameraController _cameraController;

  @override
  void dispose() {
    _cameraController.dispose();
    super.dispose();
  }

  @override
  void initState() {
    super.initState();
    initCamera(widget.cameras![0]);
  }

  Future takePicture() async {
    if (!_cameraController.value.isInitialized) {
      return null;
    }
    if (_cameraController.value.isTakingPicture) {
      return null;
    }
    try {
      await _cameraController.setFlashMode(FlashMode.off);
      XFile originalPicture = await _cameraController.takePicture();
      XFile croppedPicture = await cropSquare(originalPicture);

      Navigator.push(
          context,
          MaterialPageRoute(
              builder: (context) => PreviewPage(
                picture: croppedPicture,
              )));
    } on CameraException catch (e) {
      debugPrint('Error occured while taking picture: $e');
      return null;
    }
  }

  Future<XFile> cropSquare(XFile srcImage) async {
    var srcFilePath = srcImage.path;
    var srcFileName = Path.basenameWithoutExtension(srcFilePath);
    var srcDirname = Path.dirname(srcFilePath);
    var extension = Path.extension(srcFilePath);
    var destFileName = '${srcFileName}_33t';
    var destFilePath = '${srcDirname}/${destFileName}.${extension}';

    var bytes = await srcImage.readAsBytes();
    IMG.Image? src = IMG.decodeImage(bytes);

    if (src == null) {
      throw Exception('Could not crop image');
    }

    var cropSize = min(src.width, src.height);
    int offsetX = (src.width - cropSize) ~/ 2;
    int offsetY = (src.height - cropSize) ~/ 2;

    IMG.Image destImage = IMG.copyCrop(src, x: offsetX, y: offsetY, width: cropSize, height: cropSize);

    var jpg = IMG.encodeJpg(destImage);
    await File(destFilePath).writeAsBytes(jpg);

    return new XFile(destFilePath);
  }

  Future initCamera(CameraDescription cameraDescription) async {
    _cameraController =
        CameraController(cameraDescription, ResolutionPreset.high);
    try {
      await _cameraController.initialize().then((_) {
        if (!mounted) return;
        setState(() {});
      });
    } on CameraException catch (e) {
      debugPrint("camera error $e");
    }
  }

  Container pictureBottomBar(BuildContext context, CameraController controller) {
    const double bottomBarRadius = 24;
    var screenHeight = MediaQuery.of(context).size.height;
    var screenWidth = MediaQuery.of(context).size.width;
    var cameraHeight = screenWidth * controller.value.aspectRatio;
    var padding = MediaQuery.of(context).padding.top + MediaQuery.of(context).padding.bottom;
    var cameraOffset = screenHeight - cameraHeight - padding + bottomBarRadius;

    return Container(
      height: cameraOffset,
      decoration: const BoxDecoration(
          borderRadius: BorderRadius.vertical(top: Radius.circular(bottomBarRadius)),
          color: Colors.black
      ),
      child: Row(
          crossAxisAlignment: CrossAxisAlignment.center,
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: [
            Expanded(
                child: IconButton(
                  onPressed: takePicture,
                  iconSize: 50,
                  padding: EdgeInsets.zero,
                  constraints: const BoxConstraints(),
                  icon: const Icon(Icons.circle, color: Colors.white),
                )
            ),
          ]),
    );
  }

  Container squareFor33t(BuildContext context, CameraController controller) {
    var screenWidth = MediaQuery.of(context).size.width;
    var cameraHeight = screenWidth * controller.value.aspectRatio;
    var squareOffset = (cameraHeight / 2) - (screenWidth / 2);

    return Container(
        margin: EdgeInsets.only(top: squareOffset),
        width: screenWidth,
        height: screenWidth,
        decoration: BoxDecoration(
          border: Border.all(
            color: Colors.red,
            width: 5.0,
          ),
        ),
      );
  }

  @override
  Widget build(BuildContext context) {
    final cameraIsNotReady = !_cameraController.value.isInitialized;

    return Scaffold(
        body: SafeArea(
          child: (cameraIsNotReady)
              ? Container(
                  color: Colors.black,
                  child: const Center(child: CircularProgressIndicator()))
              : Stack(children: [
                  CameraPreview(_cameraController),
                  Positioned(
                      child: squareFor33t(context, _cameraController)),
                  Align(
                    alignment: Alignment.bottomCenter,
                    child: pictureBottomBar(context, _cameraController)),
              ]),
            ));
  }
}
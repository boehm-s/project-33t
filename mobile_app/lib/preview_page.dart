import 'dart:convert';
import 'dart:developer';

import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';


import 'package:mobile_app/model/api_result.dart';

import 'model/album.dart';

class PreviewPage extends StatefulWidget {
  const PreviewPage({Key? key, required this.picture}) : super(key: key);

  final XFile picture;

  @override
  State<PreviewPage> createState() => _PreviewPageState();
}

class _PreviewPageState extends State<PreviewPage> {
  late ApiResult<AlbumSearchResult> results;

  @override
  void initState() {
    super.initState();

    searchAlbum(widget.picture);
  }

  Future<ApiResult<AlbumSearchResult>?> searchAlbum(XFile picture) async {
    var apiUrl = dotenv.env['API_URL'];
    var url = Uri.parse("$apiUrl/search");
    var request = http.MultipartRequest('POST', url);
    request.fields.addAll({
      'all_orientations': 'true'
    });
    request.files.add(await http.MultipartFile.fromPath('image', picture.path));

    try {
      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);
      final body = response.body;
      log('res : $body');
      return ApiResult.fromJson(jsonDecode(body));
    } catch (e) {
      print(e);
      return null;
    }

  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Preview Page')),
      body: Center(
        child: Column(mainAxisSize: MainAxisSize.min, children: [
          Image.file(File(widget.picture.path), fit: BoxFit.cover, width: 250),
          const SizedBox(height: 24),
          Text(widget.picture.name)
        ]),
      ),
    );
  }
}
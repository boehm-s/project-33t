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
  late Future<AlbumSearchResult?> future_result;

  @override
  void initState() {
    super.initState();

    future_result = searchAlbum(widget.picture);
  }

  Future<AlbumSearchResult?> searchAlbum(XFile picture) async {
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
      final ApiResult<List<AlbumSearchResult>> result = ApiResult.fromJson(jsonDecode(body));
      return result.result.first;
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
          FutureBuilder(future: future_result, builder: (
              BuildContext context,
              AsyncSnapshot<AlbumSearchResult?> snapshot,
              ) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return CircularProgressIndicator();
            } else if (snapshot.connectionState == ConnectionState.done) {
              if (snapshot.hasError) {
                return const Text('Error');
              } else if (snapshot.hasData && snapshot.data != null) {
                var release = snapshot.data!.metadata.discogs_release_data;
                var album = '${release.artists_sort} - ${release.title}';

                return Text(
                    album,
                    style: const TextStyle(color: Colors.cyan, fontSize: 36)
                );
              } else {
                return const Text('Empty data');
              }
            } else {
              return Text('State: ${snapshot.connectionState}');
            }
          },)
        ]),
      ),
    );
  }
}
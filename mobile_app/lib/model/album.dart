import 'package:json_annotation/json_annotation.dart';

import 'discogs.dart';

part 'album.g.dart';

@JsonSerializable()
class AlbumSearchResult {
  final double score;
  final String filepath;
  final AlbumMetadata metadata;

  AlbumSearchResult({
    required this.score,
    required this.metadata,
    required this.filepath,
  });

  factory AlbumSearchResult.fromJson(Map<String, dynamic> json) =>
      _$AlbumSearchResultFromJson(json);

  Map<String, dynamic> toJson() => _$AlbumSearchResultToJson(this);
}

@JsonSerializable()
class AlbumMetadata {
  final String discogs_release_id;
  final String discogs_master_id;
  final DiscogsReleaseData discogs_release_data;

  AlbumMetadata({
    required this.discogs_release_id,
    required this.discogs_master_id,
    required this.discogs_release_data,
  });

  factory AlbumMetadata.fromJson(Map<String, dynamic> json) =>
      _$AlbumMetadataFromJson(json);

  Map<String, dynamic> toJson() => _$AlbumMetadataToJson(this);
}
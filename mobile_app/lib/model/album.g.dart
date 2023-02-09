// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'album.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

AlbumSearchResult _$AlbumSearchResultFromJson(Map<String, dynamic> json) =>
    AlbumSearchResult(
      score: (json['score'] as num).toDouble(),
      metadata:
          AlbumMetadata.fromJson(json['metadata'] as Map<String, dynamic>),
      filepath: json['filepath'] as String,
    );

Map<String, dynamic> _$AlbumSearchResultToJson(AlbumSearchResult instance) =>
    <String, dynamic>{
      'score': instance.score,
      'filepath': instance.filepath,
      'metadata': instance.metadata,
    };

AlbumMetadata _$AlbumMetadataFromJson(Map<String, dynamic> json) =>
    AlbumMetadata(
      discogs_release_id: json['discogs_release_id'] as String,
      discogs_master_id: json['discogs_master_id'] as String,
      discogs_release_data: DiscogsReleaseData.fromJson(
          json['discogs_release_data'] as Map<String, dynamic>),
    );

Map<String, dynamic> _$AlbumMetadataToJson(AlbumMetadata instance) =>
    <String, dynamic>{
      'discogs_release_id': instance.discogs_release_id,
      'discogs_master_id': instance.discogs_master_id,
      'discogs_release_data': instance.discogs_release_data,
    };

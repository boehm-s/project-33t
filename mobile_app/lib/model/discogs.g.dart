// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'discogs.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

DiscogsReleaseData _$DiscogsReleaseDataFromJson(Map<String, dynamic> json) =>
    DiscogsReleaseData(
      title: json['title'] as String,
      artists_sort: json['artists_sort'] as String,
    );

Map<String, dynamic> _$DiscogsReleaseDataToJson(DiscogsReleaseData instance) =>
    <String, dynamic>{
      'title': instance.title,
      'artists_sort': instance.artists_sort,
    };

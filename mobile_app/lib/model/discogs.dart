import 'package:json_annotation/json_annotation.dart';

part 'discogs.g.dart';

@JsonSerializable()
class DiscogsReleaseData {
  final String title;
  final String artists_sort; // main artist

  DiscogsReleaseData({
    required this.title,
    required this.artists_sort,
  });

  factory DiscogsReleaseData.fromJson(Map<String, dynamic> json) =>
      _$DiscogsReleaseDataFromJson(json);

  Map<String, dynamic> toJson() => _$DiscogsReleaseDataToJson(this);
}
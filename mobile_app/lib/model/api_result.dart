import 'package:json_annotation/json_annotation.dart';
import 'package:mobile_app/model/album.dart';

part 'api_result.g.dart';

@JsonSerializable()
class ApiResult<T> {
  final String status;
  @_Converter()
  final T result;

  ApiResult({
    required this.status,
    required this.result,
  });

  factory ApiResult.fromJson(Map<String, dynamic> json) =>
      _$ApiResultFromJson<T>(json);

  Map<String, dynamic> toJson() => _$ApiResultToJson(this);
}

class _Converter<T> implements JsonConverter<T, Object?> {
  const _Converter();

  static bool isAlbumSearchResult(Map<String,dynamic> json) {
    return json.containsKey('score');
  }

  @override
  T fromJson(Object? json) {
    if (json is Map<String, dynamic>) {
      if (isAlbumSearchResult(json)) {
        return AlbumSearchResult.fromJson(json) as T;
      }
    } else if (json is List) {
      if (json.isEmpty) return [] as T;

      Map<String,dynamic> firstItem = json.first as Map<String,dynamic>;

      if (isAlbumSearchResult(firstItem)) {
        return json.map((item) => AlbumSearchResult.fromJson(item)).toList() as T;
      }
    }
    throw ArgumentError.value(json, 'json', 'ApiResult._fromJson cannot handle'
        ' this JSON payload. Please add a handler to _fromJson.');
  }

  // This will only work if `object` is a native JSON type:
  //   num, String, bool, null, etc
  // Or if it has a `toJson()` function`.
  @override
  Object? toJson(T object) => object;
}

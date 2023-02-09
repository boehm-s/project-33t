// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'api_result.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

ApiResult<T> _$ApiResultFromJson<T>(Map<String, dynamic> json) => ApiResult<T>(
      status: json['status'] as String,
      result: _Converter<T>().fromJson(json['result']),
    );

Map<String, dynamic> _$ApiResultToJson<T>(ApiResult<T> instance) =>
    <String, dynamic>{
      'status': instance.status,
      'result': _Converter<T>().toJson(instance.result),
    };

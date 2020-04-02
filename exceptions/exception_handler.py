t_exception_handler(exc, context):
    # Django의 ValidationError에 대응
    if isinstance(exc, DjangoValidationError):
        if hasattr(exc, 'message_dict'):
            exc = DRFValidationError(detail={'error': exc.message_dict})
        elif hasattr(exc, 'message'):
            exc = DRFValidationError(detail={'error': exc.message})
        elif hasattr(exc, 'messages'):
            exc = DRFValidationError(detail={'error': exc.messages})
    # 클라이언트에서 status및 code활용
    response = exception_handler(exc, context)
    if response:
        response.data['status'] = response.status_code
        # Exception에 'code'가 존재할 경우 해당 내용
        # 없으면 Response의 ErrorDetail이 가지고 있는 'code'값
        response.data['code'] = getattr(exc, 'code', getattr(exc, 'default_code', None)) or response.data['detail'].code
    return response
class ConflictValidationException(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = '데이터가 이미 변경되었습니다. 새로고침 후 다시 시도하세요.'
    default_code = 'invalid'

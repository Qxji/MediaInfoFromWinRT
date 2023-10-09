# Many thanks to the original answer to a stackexchange answer I adapted and made working again (Did not change much
# honestly):
# https://stackoverflow.com/questions/65011660/how-can-i-get-the-title-of-the-currently-playing-media-in-windows-10-with-python#answer-66037406

import asyncio

from winsdk.windows.media.control import \
    GlobalSystemMediaTransportControlsSessionManager as MediaManager
from winsdk.windows.storage.streams import \
    DataReader, Buffer, InputStreamOptions


async def get_media_info():
    sessions = await MediaManager.request_async()

    current_session = sessions.get_current_session()
    if current_session:  # there needs to be a media session running
        info = await current_session.try_get_media_properties_async()

        # song_attr[0] != '_' ignores system attributes
        info_dict = {song_attr: info.__getattribute__(song_attr) for song_attr in dir(info) if song_attr[0] != '_'}

        # converts winrt vector to list
        info_dict['genres'] = list(info_dict['genres'])

        return info_dict

    # It could be possible to select a program from a list of current
    # available ones. I just haven't implemented this here for my use case.
    # See references for more information.
    raise Exception('No session running')


async def read_stream_into_buffer(stream_ref, buffer):
    readable_stream = await stream_ref.open_read_async()
    readable_stream.read_async(buffer, buffer.capacity, InputStreamOptions.READ_AHEAD)


if __name__ == '__main__':
    current_media_info = asyncio.run(get_media_info())
    # create the current_media_info dict with the earlier code first
    thumb_stream_ref = current_media_info['thumbnail']
    # 5MB (5 million byte) buffer - thumbnail unlikely to be larger
    thumb_read_buffer = Buffer(5000000)
    # copies data from data stream reference into buffer created above
    asyncio.run(read_stream_into_buffer(thumb_stream_ref, thumb_read_buffer))
    # reads data (as bytes) from buffer
    buffer_reader = DataReader.from_buffer(thumb_read_buffer)
    byte_buffer = buffer_reader.read_buffer(buffer_reader.unconsumed_buffer_length)
    with open('media_thumb.jpg', 'wb+') as fobj:
        fobj.write(bytearray(byte_buffer))

    print(current_media_info)

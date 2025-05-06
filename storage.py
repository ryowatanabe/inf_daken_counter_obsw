from os import mkdir
from os.path import join,exists
import io
from google.cloud import storage
import uuid
from PIL import Image,ImageDraw

from threading import Thread
from logging import getLogger

logger = getLogger().getChild('storage')
logger.debug('loaded storage.py')

from service_account_info import service_account_info
from define import define

bucket_name_informations = 'bucket-inf-notebook-informations'
bucket_name_details = 'bucket-inf-notebook-details'
bucket_name_musicselect = 'bucket-inf-notebook-musicselect'
bucket_name_resources = 'bucket-inf-notebook-resources'

informations_dirname = 'informations'
details_dirname = 'details'
musicselect_dirname = 'musicselect'

result_rivalname_fillbox = (
    (
        define.details_graphtarget_name_area[0],
        define.details_graphtarget_name_area[1]
    ),
    (
        define.details_graphtarget_name_area[2],
        define.details_graphtarget_name_area[3]
    )
)

musicselect_rivals_fillbox = (
    (
        define.musicselect_rivals_name_area[0],
        define.musicselect_rivals_name_area[1],
    ),
    (
        define.musicselect_rivals_name_area[2],
        define.musicselect_rivals_name_area[3]
    )

)

"""
storage.py

このスクリプトは、Google Cloud Storage を利用して画像やリソースを管理するためのものです。
主に、画像のアップロード、ダウンロード、削除を行います。

主な機能:
- バケットへの接続
- 画像やリソースのアップロードとダウンロード
- 必要に応じた画像のトリミングや加工
"""

class StorageAccessor():
    """
    Google Cloud Storage を操作するためのクラス。
    バケットへの接続や、画像・リソースのアップロード、ダウンロードを行います。
    """
    client = None
    bucket_informations = None
    bucket_details = None
    bucket_musicselect = None
    bucket_resources = None
    blob_musics = None

    def connect_client(self):
        """
        Google Cloud Storage クライアントに接続します。
        """
        if self.client is not None:
            return
        
        if service_account_info is None:
            logger.info('no define service_account_info')
            return
        
        try:
            self.client = storage.Client.from_service_account_info(service_account_info)
            logger.debug('connect client')
        except Exception as ex:
            logger.error(f'Failed to connect client: {ex}')
            self.client = None

    def connect_bucket_informations(self):
        """
        informations バケットに接続します。
        """
        if self.client is None:
            self.connect_client()
        if self.client is None:
            return
        
        try:
            self.bucket_informations = self.client.get_bucket(bucket_name_informations)
            logger.debug('connect bucket informations')
        except Exception as ex:
            logger.error(ex)

    def connect_bucket_details(self):
        """
        details バケットに接続します。
        """
        if self.client is None:
            self.connect_client()
        if self.client is None:
            return
        
        try:
            self.bucket_details = self.client.get_bucket(bucket_name_details)
            logger.debug('connect bucket details')
        except Exception as ex:
            logger.error(ex)
    
    def connect_bucket_musicselect(self):
        """
        musicselect バケットに接続します。
        """
        if self.client is None:
            self.connect_client()
        if self.client is None:
            return
        
        try:
            self.bucket_musicselect = self.client.get_bucket(bucket_name_musicselect)
            logger.debug('connect bucket musicselect')
        except Exception as ex:
            logger.error(ex)
    
    def connect_bucket_resources(self):
        """
        resources バケットに接続します。
        """
        if self.client is None:
            self.connect_client()
        if self.client is None:
            return
        
        try:
            self.bucket_resources = self.client.get_bucket(bucket_name_resources)
            logger.debug('connect bucket resources')
        except Exception as ex:
            logger.error(ex)

    def upload_image(self, blob, image):
        """
        指定されたバケットに画像をアップロードします。

        引数:
        - blob: アップロード先のバケットオブジェクト
        - image: アップロードする画像 (PIL.Image)
        """
        bytes = io.BytesIO()
        image.save(bytes, 'PNG')
        blob.upload_from_file(bytes, True)
        bytes.close()

    def upload_informations(self, object_name, image):
        """
        informations バケットに画像をアップロードします。

        引数:
        - object_name: アップロードするオブジェクト名
        - image: アップロードする画像 (PIL.Image)
        """
        if self.bucket_informations is None:
            self.connect_bucket_informations()
        if self.bucket_informations is None:
            return

        try:
            blob = self.bucket_informations.blob(object_name)
            self.upload_image(blob, image)
            logger.debug(f'upload information image {object_name}')
        except Exception as ex:
            logger.error(ex)

    def upload_details(self, object_name, image):
        """
        details バケットに画像をアップロードします。

        引数:
        - object_name: アップロードするオブジェクト名
        - image: アップロードする画像 (PIL.Image)
        """
        if self.bucket_details is None:
            self.connect_bucket_details()
        if self.bucket_details is None:
            return

        try:
            blob = self.bucket_details.blob(object_name)
            self.upload_image(blob, image)
            logger.debug(f'upload details image {object_name}')
        except Exception as ex:
            logger.error(ex)

    def upload_musicselect(self, object_name, image):
        """
        musicselect バケットに画像をアップロードします。

        引数:
        - object_name: アップロードするオブジェクト名
        - image: アップロードする画像 (PIL.Image)
        """
        if self.bucket_musicselect is None:
            self.connect_bucket_musicselect()
        if self.bucket_musicselect is None:
            return

        try:
            blob = self.bucket_musicselect.blob(object_name)
            self.upload_image(blob, image)
            logger.debug(f'upload musicselect image {object_name}')
        except Exception as ex:
            logger.error(ex)

    def start_uploadcollection(self, result, image, force):
        """
        収集画像をアップロードします。

        引数:
        - result: 対象のリザルト (Result クラス)
        - image: 対象のリザルト画像 (PIL.Image)
        - force: 強制アップロードのフラグ (bool)

        戻り値:
        - informations と details の両方をアップロードしたかどうか (bool)
        """
        self.connect_client()
        if self.client is None:
            return
        
        object_name = f'{uuid.uuid1()}.png'

        informations_trim = force
        details_trim = force

        if result.informations is None:
            informations_trim = True
        else:
            if result.informations.play_mode is None:
                informations_trim = True
            if result.informations.difficulty is None:
                informations_trim = True
            if result.informations.level is None:
                informations_trim = True
            if result.informations.music is None:
                informations_trim = True

        if result.details is None:
            details_trim = True
        else:
            if result.details.clear_type is None or result.details.clear_type.current is None:
                details_trim = True
            if result.details.dj_level is None or result.details.dj_level.current is None:
                details_trim = True
            if result.details.score is None or result.details.score.current is None:
                details_trim = True
            if result.details.graphtarget is None:
                details_trim = True

        if informations_trim:
            trim = image.crop(define.informations_trimarea)
            Thread(target=self.upload_informations, args=(object_name, trim,)).start()
        if details_trim:
            play_side = result.play_side
            trim = image.crop(define.details_trimarea[play_side])
            image_draw = ImageDraw.Draw(trim)
            image_draw.rectangle(result_rivalname_fillbox, fill=0)
            Thread(target=self.upload_details, args=(object_name, trim,)).start()
        
        return informations_trim and details_trim
    
    def start_uploadmusicselect(self, image):
        """
        選曲画面の収集画像をアップロードします。

        引数:
        - image: 対象のリザルト画像 (PIL.Image)
        """
        self.connect_client()
        if self.client is None:
            return
        
        object_name = f'{uuid.uuid1()}.png'

        trim = image.crop(define.musicselect_trimarea)
        image_draw = ImageDraw.Draw(trim)
        image_draw.rectangle(musicselect_rivals_fillbox, fill=0)
        Thread(target=self.upload_musicselect, args=(object_name, trim,)).start()
    
    def upload_resource(self, resourcename, targetfilepath):
        """
        resources バケットにリソースをアップロードします。

        引数:
        - resourcename: アップロードするリソース名
        - targetfilepath: アップロードするファイルのパス
        """
        if self.bucket_resources is None:
            self.connect_bucket_resources()
        if self.bucket_resources is None:
            return

        try:
            blob = self.bucket_resources.blob(resourcename)
            blob.upload_from_filename(targetfilepath)
            logger.debug(f'upload resource {targetfilepath}')
        except Exception as ex:
            logger.error(ex)
    
    def get_resource_timestamp(self, resourcename):
        """
        指定されたリソースのタイムスタンプを取得します。

        引数:
        - resourcename: 対象のリソース名

        戻り値:
        - タイムスタンプ (str) または None
        """
        if self.bucket_resources is None:
            self.connect_bucket_resources()
        if self.bucket_resources is None:
            return False

        try:
            blob = self.bucket_resources.get_blob(resourcename)
            return str(blob.updated)
        except Exception as ex:
            logger.error(ex)
        
        return None
    
    def download_resource(self, resourcename, targetfilepath):
        """
        resources バケットからリソースをダウンロードします。

        引数:
        - resourcename: ダウンロードするリソース名
        - targetfilepath: 保存先のファイルパス

        戻り値:
        - ダウンロード成功 (bool)
        """
        if self.bucket_resources is None:
            self.connect_bucket_resources()
        if self.bucket_resources is None:
            return False
        
        blob = self.bucket_resources.get_blob(resourcename)

        try:
            blob.download_to_filename(targetfilepath)
            logger.debug('download resource {targetfilepath}')
        except Exception as ex:
            logger.error(ex)
            return False
        
        return True

    def save_image(self, basepath, blob):
        """
        バケット内の画像を保存します。

        引数:
        - basepath: 保存先のディレクトリパス
        - blob: 対象のバケットオブジェクト
        """
        if not exists(basepath):
            mkdir(basepath)
        
        image_bytes = blob.download_as_bytes()
        image = Image.open(io.BytesIO(image_bytes))
        filepath = join(basepath, blob.name)
        image.save(filepath)

    def download_and_delete_all(self, basedir):
        """
        バケット内のすべての画像をダウンロードし、削除します。

        引数:
        - basedir: 保存先のディレクトリパス
        """
        self.connect_client()
        if self.client is None:
            print('connect client failed')
            return

        if not exists(basedir):
            mkdir(basedir)

        informations_dirpath = join(basedir, informations_dirname)
        details_dirpath = join(basedir, details_dirname)
        musicselect_dirpath = join(basedir, musicselect_dirpath)

        count = 0
        blobs = self.client.list_blobs(bucket_name_informations)
        for blob in blobs:
            self.save_image(informations_dirpath, blob)
            blob.delete()
            count += 1

        blobs = self.client.list_blobs(bucket_name_details)
        for blob in blobs:
            self.save_image(details_dirpath, blob)
            blob.delete()
            count += 1

        blobs = self.client.list_blobs(bucket_name_musicselect)
        for blob in blobs:
            self.save_image(musicselect_dirpath, blob)
            blob.delete()
            count += 1

        print(f'download count: {count}')

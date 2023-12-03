# 视频特效平台

版本：`v1.0`

环境信息：
* python3.10.12
* Poetry1.6.1

## 接口文档

本文档描述了合成服务的HTTP接口。响应状态以status_code为判断依据，成功为200，失败为400/404/500等。
响应结果在非文件的情况下均为json格式，`Content-Type: application/json`。

```text
{
  "code": 10000,
  "message": "成功或者错误信息",
  "data": {},  // 响应结果
}
```
状态码枚举如下
* 0     请求成功
* 10000	参数错误
* 10001	合成失败
* 10002	任务提交失败
* 10003	文件找不到
* 10100	内部错误

### 文件上传
文件上传接口，主要用于提前将素材上传到合成服务器，避免后续合成任务每次上传重复文件数据。
```text
POST /v1.0/zone/{ZONE}/asset HTTP/1.1
```
*ZONE 为景区标识符，由调用方确保唯一，注意不要包含特殊字符，以免产生未知错误。如无特殊说明，其它接口ZONE均参考此说明*。

请求内容包含待上传的文件数据，通过`Content-Type: multipart/form-data; boundary=XXXX`方式支持多个文件同时上传。

`name`以及`filename`需要同时存在，`name`与合成规则中的`name`字段对应，`filename`需要包含文件的完整扩展名。如果之前已经上传过相同的`name`文件，文件将会被覆盖。

**请求示例**

```text
POST /v1.0/zone/{ZONE}/synth/oneshot HTTP/1.1
Content-Length: 10000
Content-Type: multipart/form-data; boundary=${Boundary}

--${Boundary}
Content-Disposition: form-data; name="prelude_01"; filename="preclude_01.mp4"
Content-Type: application/octet-stream

preclude_01视频数据...
--${Boundary}
Content-Disposition: form-data; name="camera_01"; filename="camera_01.mp4"
Content-Type: application/octet-stream

camera_01视频数据...
```

**响应**
```text
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "name": "epilog_01", //唯一标识，与上传时的 name 对应，合成规则中指向此名。
      "size": 9956701 //文件大小
    },
    {
      "name": "bgm_01",
      "size": 781988
    },
    {
      "name": "prelude_01",
      "size": 6249432
    }
  ]
}
```

### 文件列表
文件列表接口，列出服务器中已预先上传的文件信息。
文件上传接口，主要用于提前将素材上传到合成服务器，避免后续合成任务每次上传重复文件数据。
```text
GET /v1.0/zone/{ZONE}/asset
```

**响应**
```text
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "name": "epilog_01",
      "size": 9956701
    },
    {
      "name": "bgm_01",
      "size": 781988
    }
  ]
}
```

### 同步合成

同步合成接口，返回时则表示合成完毕。合成服务会配置同步合成任务的数量，同步请求有可能响应时间较慢导致超时，可考虑使用`异步合成`接口。
```
POST /v1.0/zone/{ZONE}/synth/oneshot
```
请求内容包含两部分：合成规则以及视频数据。请求头部使用`Content-Type: multipart/form-data; boundary=XXXX`进行数据上传。

**合成规则**

合成规则为`json`格式，`name`需设置为`rules`。 
clips为合成规则，需要保证所有视频片段具备相同的流（编码、TimeBase），排列顺序影响合成的结果
music为背景音乐，合成时自动循环。

**视频数据**

`name`以及`filename`需要同时存在，`name`与合成规则中的`name`字段对应，`filename`需要包含文件的完整扩展名。

**请求示例**
```text
POST /v1.0/zone/aly/synth/oneshot HTTP/1.1
Content-Length: 10000
Content-Type: multipart/form-data; boundary=${Boundary}

--${Boundary}
Content-Disposition: form-data; name="rules"
Content-Type: application/json

{
  "clips": [
    {
      "name": "video_1",
      "vfx": [
        {
          "code": "VFXSlowMotion",
          "params": {"begin_sec":  1}
        },
        {
          "code": "VFXFrameFreeze",
          "params": {"begin_sec":  1}
        }
      ]
    },
    {
      "name": "video_2",
      "vfx": null
    }
  ],
  "music": {
    "name": "music_1"
  }
}
--${Boundary}
Content-Disposition: form-data; name="video_1"; filename="video_1.mp4"
Content-Type: application/octet-stream

video_1视频数据...
--${Boundary}
Content-Disposition: form-data; name="video_2"; filename="video_2.mp4"
Content-Type: application/octet-stream

video_2视频数据...
--${Boundary}
Content-Disposition: form-data; name="music_1"; filename="music_1.mp3"
Content-Type: application/octet-stream

music_1音频数据...
--${Boundary}
```

**响应**
```text
{
  "code": 0,
  "message": "success",
  "data": {
    "cos": {
      "Bucket": "vfxs-test-1318254791",
      "Key": "xxx.mp4"
      "Location": "视频地址"
    }
  }
}
```

### 异步合成
待开发

## 特效规则
特效在在合成接口中的rules中指定，每一个视频可以绑定多个特效。
* name: 待处理的人物视频
* vfx: 特效参数。如果没有vfx则会从预上传素材获取数据，如果vfx=null则代表不做特效处理
* code: 特效的编码，用于指定使用哪种特效。
* params: 使用该特效的参数，每个特效的参数不同。
```text
{
  "name": "prelude_01",
  "vfx": [
      {
        "code": "VFXSlowMotion",
        "params": {"k1": "v1"}
     }
  ]
}
```
每个特效具体的code及参数如下

**画框定格（VFXFrameFreeze）**

| 参数 | 类型    | 必选 | 默认值 | 说明 |
| -- |-------|----|-----| -- |
| begin_sec | float | 是  | 无   | 特效开始时间 |

**慢动作（VFXSlowMotion）**

| 参数 | 类型  | 必选 | 默认值 | 说明 |
| -- |-----|----|-----| -- |
| begin_sec | float | 是  | 无   | 慢放开始时间 |

**RGB震动（VFXRGBShake）**

| 参数 | 类型  | 必选 | 默认值 | 说明 |
| -- |-----|----|-----| -- |
| begin_sec | float | 是  | 无   | 慢放开始时间 |

**取景框慢动作（VFXViewfinderSlowAction）**

| 参数 | 类型    | 必选 | 默认值 | 说明 |
| -- |-------|----|-----| -- |
| main_char | str   | 是  | 无   | 主角人脸图片 |
| cosine_similar_thresh | float | 否  | 0.2 | 人脸相似度阈值 |

**C位放大镜（VFXEnlargeFaces）**

| 参数 | 类型    | 必选 | 默认值 | 说明     |
| -- |-------|----|-----|--------|
| main_char | str   | 是  | 无   | 主角人脸图片 |
| cosine_similar_thresh | float | 否  | 0.2 | 人脸相似度阈值 |

**路人虚化（VFXPassersbyBlurred）**

| 参数 | 类型    | 必选 | 默认值 | 说明     |
| -- |-------|----|-----|--------|
| main_char | str   | 是  | 无   | 主角人脸图片 |
| cosine_similar_thresh | float | 否  | 0.2 | 人脸相似度阈值 |

**变焦（VFXPersonFollowFocus）**

| 参数 | 类型    | 必选 | 默认值 | 说明     |
| -- |-------|----|-----|--------|
| main_char | str   | 是  | 无   | 主角人脸图片 |
| cosine_similar_thresh | float | 否  | 0.2 | 人脸相似度阈值 |

**MV封面（VFXMVCover）**

| 参数 | 类型     | 必选 | 默认值 | 说明 |
| -- |--------|----|-----| -- |
| begin_sec | float    | 是  | 无   | 特效开始时间 |

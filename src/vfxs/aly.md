# 接口文档

## 历史
* 2023-08-10
	* 增加景区限制
* 2023-07-25
	* 增加文件列表接口
	* 补充文件预上传响应说明
* 2023-07-24
	* 增加文件预上传功能
* 2023-07-17
	* 初始版本

## 介绍

本文档描述了合成服务的HTTP接口，响应成功状态码为`200`；如出现请求失败，状态码会以400/404/500返回，且失败信息会以`json`的形式返回，如下：

```
{
    "code": 10000, //错误码
    "message": "Invalid task id" //错误信息
}

错误码：
10000	参数错误
10001	合成失败
10002	任务提交失败
10003	文件找不到
10100	内部错误
```

当前版本号为：`1.0`

## 文件上传

### 描述

文件上传接口，主要用于提前将素材上传到合成服务器，避免后续合成任务每次上传重复文件数据。

### URI

`/1.0/zone/{ZONE}/asset`

### 方法

`POST`

### 请求

***ZONE 为景区标识符，由调用方确保唯一，注意不要包含特殊字符，以免产生未知错误。如无特殊说明，其它接口ZONE均参考此说明***。

请求内容包含待上传的文件数据，通过`Content-Type: multipart/form-data; boundary=XXXX`方式支持多个文件同时上传。

`name`以及`filename`需要同时存在，`name`与合成规则中的`name`字段对应，`filename`需要包含文件的完整扩展名。如果之前已经上传过相同的`name`文件，文件将会被覆盖。

```
Content-Disposition: form-data; name="prelude_01"; filename="preclude_01.mp4"
Content-Type: application/octet-stream

preclude_01视频数据...
```

* 示例

```
POST /1.0/zone/{ZONE}/synth/oneshot HTTP/1.1
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
--${Boundary}
Content-Disposition: form-data; name="camera_02"; filename="camera_02.mp4"
Content-Type: application/octet-stream

camera_02视频数据...
--${Boundary}
Content-Disposition: form-data; name="epilog_01"; filename="epilog_01.mp4"
Content-Type: application/octet-stream

epilog_01视频数据...
--${Boundary}
Content-Disposition: form-data; name="bgm_01"; filename="bgm_01.mp3"
Content-Type: application/octet-stream

bgm_01音频数据...
--${Boundary}
```

### 响应

响应数据为`json`格式，`Content-Type: application/json`，只返回成功上传的文件

```
[
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
  },
  {
    "name": "camera_01",
    "size": 9125673
  },
  {
    "name": "camera_02",
    "size": 7787006
  }
]
```

## 文件列表

### 描述

文件列表接口，列出服务器中已预先上传的文件信息。

### URI

`/1.0/zone/{ZONE}/asset`

### 方法

`GET`

### 请求

无

### 响应

响应数据为`json`格式，`Content-Type: application/json`，返回所有文件列表

```
[
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
  },
  {
    "name": "camera_01",
    "size": 9125673
  },
  {
    "name": "camera_02",
    "size": 7787006
  }
]
```

## 同步合成

### 描述

同步合成接口，返回时则表示合成完毕。合成服务会配置同步合成任务的数量，同步请求有可能响应时间较慢导致超时，可考虑使用`异步合成`接口。

### URI

`/1.0/zone/{ZONE}/synth/oneshot`

### 方法

`POST`

### 请求

请求内容包含两部分：合成规则以及视频数据。请求头部使用`Content-Type: multipart/form-data; boundary=XXXX`进行数据上传。

* 合成规则

合成规则为`json`格式，`name`需设置为`rules`

```
Content-Disposition: form-data; name="rules"
Content-Type: application/json

{
    "clips": [ //视频片段，需要保证所有视频片段具备相同的流（编码、TimeBase），排列顺序影响合成的结果
        {
            "name": "prelude_01",  //片段名，该名称和上传视频数据时候的 name 一致，如果通过文件上传接口提前上传了文件，下方的视频数据中则无须再次上传
        },
        {
            "name": "camera_01"
        },
        {
            "name": "camera_02"
        },
        {
            "name": "epilog_01"
        },
    ],
    "music": { //背景音乐，合成时自动循环
        "name": "bgm_01" //背景音乐名，该名称和上传视频数据时候的 name 一致
    }
}
```

* 视频数据

`name`以及`filename`需要同时存在，`name`与合成规则中的`name`字段对应，`filename`需要包含文件的完整扩展名。

```
Content-Disposition: form-data; name="prelude_01"; filename="preclude_01.mp4"
Content-Type: application/octet-stream

preclude_01视频数据...
```

* 示例

```
POST /1.0/zone/aly/synth/oneshot HTTP/1.1
Content-Length: 10000
Content-Type: multipart/form-data; boundary=${Boundary}

--${Boundary}
Content-Disposition: form-data; name="rules"
Content-Type: application/json

{
    "clips": [
        {
            "name": "prelude_01", 
        },
        {
            "name": "camera_01"
        },
        {
            "name": "camera_02"
        },
        {
            "name": "epilog_01"
        },
    ],
    "music": {
        "name": "bgm_01"
    }
}
--${Boundary}
Content-Disposition: form-data; name="prelude_01"; filename="preclude_01.mp4"
Content-Type: application/octet-stream

preclude_01视频数据...
--${Boundary}
Content-Disposition: form-data; name="camera_01"; filename="camera_01.mp4"
Content-Type: application/octet-stream

camera_01视频数据...
--${Boundary}
Content-Disposition: form-data; name="camera_02"; filename="camera_02.mp4"
Content-Type: application/octet-stream

camera_02视频数据...
--${Boundary}
Content-Disposition: form-data; name="epilog_01"; filename="epilog_01.mp4"
Content-Type: application/octet-stream

epilog_01视频数据...
--${Boundary}
Content-Disposition: form-data; name="bgm_01"; filename="bgm_01.mp3"
Content-Type: application/octet-stream

bgm_01音频数据...
--${Boundary}
```

### 响应

响应数据为`json`格式，`Content-Type: application/json`

```
{
    "url": "/1.0/zone/aly/artifact/xxxxx" //下载URI，默认合成结果保留24小时（具体以实际配置为准）
}
```

## 异步合成

### 描述

异步合成接口，提交数据并返回任务ID，后续可通过任务状态查询接口获取任务状态。

### URI

`/1.0/zone/{ZONE}/synth/task`

### 方法

`POST`

### 请求

请求内容与`同步`接口一致，具体参考 `/1.0/zone/{ZONE}/synth/oneshot`

### 响应

响应数据为`json`格式，`Content-Type: application/json`

```
{
    "task_id": "xxxxxxxxx" //合成任务ID
}
```

## 任务状态

### 描述

查询指定任务状态。

### URI

`/1.0/zone/{ZONE}/synth/task/{TASK_ID}`

### 方法

`GET`

### 请求

无

### 响应

响应数据为`json`格式，`Content-Type: application/json`

```
{
    "task_id": "xxxxxxxxx", //合成任务ID
    "status": 0, // 任务状态 0 - 待合成，1 - 合成中，2 - 合成成功, 3 - 合成失败
    "url": "/1.0/zone/aly/artifact/xxxxx", //下载URI，仅当合成成功时有效，默认合成结果保留24小时（具体以实际配置为准）
    "create_time": 1689562043, //任务创建时间，UTC时间戳
    "start_time": 1689562048, //任务开始时间，UTC时间戳
    "finish_time": 1689562050 //任务结束时间（成功或失败），UTC时间戳，仅当合成完成（成功或失败）时有效
}
```

## 结果下载

### 描述

下载合成文件

### URI

`/1.0/zone/{ZONE}/artifact/{ID}`

### 方法

`GET`

### 请求

无

### 响应

合成文件数据内容
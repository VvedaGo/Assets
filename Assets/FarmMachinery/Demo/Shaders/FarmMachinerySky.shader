Shader "FarmMachinery/Demo/URP Panorama Sky"
{
    // Demo sky of the Farm Machinery scenes: a latitude-longitude panorama (T_FarmMachinery_SkyPanorama, vertical gradient) —
    // the series solution of the Farm Nature demo sky, own copy so the pack has no dependency on Farm Nature.
    Properties
    {
        _MainTex ("Sky Panorama", 2D) = "white" {}
        _Exposure ("Exposure", Range(0, 4)) = 1
        _Rotation ("Rotation", Range(0, 360)) = 0
    }
    SubShader
    {
        Tags { "Queue"="Background" "RenderType"="Background" "PreviewType"="Skybox" "RenderPipeline"="UniversalPipeline" }
        Cull Off
        ZWrite Off
        Pass
        {
            Name "Sky"
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma target 3.0
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            TEXTURE2D(_MainTex);
            SAMPLER(sampler_MainTex);
            CBUFFER_START(UnityPerMaterial)
                float4 _MainTex_ST;
                float _Exposure;
                float _Rotation;
            CBUFFER_END

            struct Attributes { float4 positionOS : POSITION; };
            struct Varyings { float4 positionCS : SV_POSITION; float3 direction : TEXCOORD0; };

            Varyings Vert(Attributes input)
            {
                Varyings output;
                float angle = radians(_Rotation);
                float sine, cosine;
                sincos(angle, sine, cosine);
                float3 position = input.positionOS.xyz;
                position.xz = float2(cosine * position.x - sine * position.z, sine * position.x + cosine * position.z);
                output.positionCS = TransformObjectToHClip(position);
                output.positionCS.z = output.positionCS.w * UNITY_RAW_FAR_CLIP_VALUE;
                output.direction = input.positionOS.xyz;
                return output;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                float3 direction = normalize(input.direction);
                float2 uv = float2(0.5 - atan2(direction.z, direction.x) / TWO_PI, 1.0 - acos(clamp(direction.y, -1.0, 1.0)) / PI);
                half3 color = SAMPLE_TEXTURE2D(_MainTex, sampler_MainTex, uv).rgb;
                return half4(color * _Exposure, 1.0);
            }
            ENDHLSL
        }
    }
    Fallback Off
}

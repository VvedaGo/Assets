Shader "FarmMarketStarter/Gradient Sky"
{
    Properties
    {
        _ZenithColor ("Zenith Color", Color) = (0.30, 0.50, 0.86, 1)
        _HorizonColor ("Horizon Color", Color) = (0.80, 0.89, 0.97, 1)
        _GroundColor ("Ground Color", Color) = (0.62, 0.66, 0.55, 1)
        _Exponent ("Gradient Exponent", Range(0.1, 4)) = 0.7
        _Exposure ("Exposure", Range(0, 3)) = 1.1
    }

    SubShader
    {
        Tags { "RenderPipeline" = "UniversalPipeline" "Queue" = "Background" "RenderType" = "Background" "PreviewType" = "Skybox" }
        Cull Off
        ZWrite Off

        Pass
        {
            Name "GradientSky"

            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            CBUFFER_START(UnityPerMaterial)
                half4 _ZenithColor;
                half4 _HorizonColor;
                half4 _GroundColor;
                half _Exponent;
                half _Exposure;
            CBUFFER_END

            struct Attributes
            {
                float4 positionOS : POSITION;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 direction : TEXCOORD0;
            };

            Varyings vert(Attributes input)
            {
                Varyings output;
                output.positionCS = TransformObjectToHClip(input.positionOS.xyz);
                output.direction = input.positionOS.xyz;
                return output;
            }

            half4 frag(Varyings input) : SV_Target
            {
                float height = normalize(input.direction).y;
                half3 sky = lerp(_HorizonColor.rgb, _ZenithColor.rgb, pow(saturate(height), _Exponent));
                half3 ground = lerp(_HorizonColor.rgb, _GroundColor.rgb, saturate(-height * 4.0));
                return half4((height >= 0 ? sky : ground) * _Exposure, 1);
            }
            ENDHLSL
        }
    }
}

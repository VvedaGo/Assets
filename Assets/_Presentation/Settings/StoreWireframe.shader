Shader "Hidden/FarmAnimals/StoreWireframe"
{
    SubShader
    {
        Tags { "RenderPipeline"="UniversalPipeline" "RenderType"="Opaque" }
        Pass
        {
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                float3 barycentric : TEXCOORD0;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 normalWS : TEXCOORD0;
                float3 barycentric : TEXCOORD1;
            };

            Varyings Vert(Attributes input)
            {
                Varyings output;
                output.positionCS = TransformObjectToHClip(input.positionOS.xyz);
                output.normalWS = TransformObjectToWorldNormal(input.normalOS);
                output.barycentric = input.barycentric;
                return output;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                float3 width = fwidth(input.barycentric) * 1.45;
                float3 fill = smoothstep(width * .3, width, input.barycentric);
                float interior = min(min(fill.x, fill.y), fill.z);
                half key = saturate(dot(normalize(input.normalWS), normalize(float3(-.5, 1, .7))));
                half3 surface = lerp(half3(.055, .105, .115), half3(.14, .27, .28), key);
                return half4(lerp(half3(.42, .69, .67), surface, interior), 1);
            }
            ENDHLSL
        }
    }
}
